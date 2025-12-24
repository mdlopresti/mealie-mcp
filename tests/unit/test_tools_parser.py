"""Unit tests for parser tools (src/tools/parser.py).

Tests ingredient parsing functionality including single and batch parsing,
edge cases, and error handling. All tests use mocked MealieClient.
"""

import json
import pytest
from unittest.mock import Mock
from src.tools.parser import parser_ingredient, parser_ingredients_batch
from tests.unit.builders import build_parsed_ingredient


class TestParserIngredient:
    """Tests for single ingredient parsing."""

    def test_parse_simple_ingredient(self):
        """Test parsing a simple ingredient string."""
        # Mock client
        mock_client = Mock()
        mock_client.parse_ingredient.return_value = build_parsed_ingredient(
            input_text="2 cups flour",
            quantity=2.0,
            unit="cup",
            food="flour"
        )

        # Patch MealieClient in the module
        from src.tools import parser
        original_client = parser.MealieClient
        parser.MealieClient = Mock(return_value=mock_client)
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        try:
            result = parser_ingredient("2 cups flour")
            result_dict = json.loads(result)

            # Verify structure
            assert "input" in result_dict
            assert "ingredient" in result_dict
            assert "confidence" in result_dict

            # Verify values
            assert result_dict["input"] == "2 cups flour"
            assert result_dict["ingredient"]["quantity"] == 2.0
            assert result_dict["ingredient"]["unit"]["name"] == "cup"
            assert result_dict["ingredient"]["food"]["name"] == "flour"
        finally:
            parser.MealieClient = original_client

    def test_parse_ingredient_with_fraction(self):
        """Test parsing ingredient with fractional quantity."""
        mock_client = Mock()
        mock_client.parse_ingredient.return_value = build_parsed_ingredient(
            input_text="1/2 cup sugar",
            quantity=0.5,
            unit="cup",
            food="sugar"
        )

        from src.tools import parser
        original_client = parser.MealieClient
        parser.MealieClient = Mock(return_value=mock_client)
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        try:
            result = parser_ingredient("1/2 cup sugar")
            result_dict = json.loads(result)

            assert result_dict["ingredient"]["quantity"] == 0.5
            assert result_dict["ingredient"]["unit"]["name"] == "cup"
            assert result_dict["ingredient"]["food"]["name"] == "sugar"
        finally:
            parser.MealieClient = original_client

    def test_parse_ingredient_with_teaspoon(self):
        """Test parsing ingredient with teaspoon measurement."""
        mock_client = Mock()
        mock_client.parse_ingredient.return_value = build_parsed_ingredient(
            input_text="1 tsp salt",
            quantity=1.0,
            unit="teaspoon",
            food="salt"
        )

        from src.tools import parser
        original_client = parser.MealieClient
        parser.MealieClient = Mock(return_value=mock_client)
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        try:
            result = parser_ingredient("1 tsp salt")
            result_dict = json.loads(result)

            assert result_dict["ingredient"]["quantity"] == 1.0
            assert "teaspoon" in result_dict["ingredient"]["unit"]["name"].lower() or \
                   "tsp" in result_dict["ingredient"]["unit"]["name"].lower()
        finally:
            parser.MealieClient = original_client

    def test_parse_ingredient_with_note(self):
        """Test parsing ingredient with additional notes."""
        mock_client = Mock()
        parsed = build_parsed_ingredient(
            input_text="2 cups flour, sifted",
            quantity=2.0,
            unit="cup",
            food="flour"
        )
        parsed["ingredient"]["note"] = "sifted"
        mock_client.parse_ingredient.return_value = parsed

        from src.tools import parser
        original_client = parser.MealieClient
        parser.MealieClient = Mock(return_value=mock_client)
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        try:
            result = parser_ingredient("2 cups flour, sifted")
            result_dict = json.loads(result)

            assert result_dict["ingredient"]["quantity"] == 2.0
            assert result_dict["ingredient"]["note"] == "sifted"
        finally:
            parser.MealieClient = original_client

    def test_parse_ingredient_with_brute_parser(self):
        """Test parsing with brute force parser."""
        mock_client = Mock()
        mock_client.parse_ingredient.return_value = build_parsed_ingredient()

        from src.tools import parser
        original_client = parser.MealieClient
        parser.MealieClient = Mock(return_value=mock_client)
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        try:
            result = parser_ingredient("2 cups flour", parser="brute")

            # Verify parser parameter was passed
            mock_client.parse_ingredient.assert_called_once_with(
                ingredient="2 cups flour",
                parser="brute"
            )
        finally:
            parser.MealieClient = original_client

    def test_parse_ingredient_empty_string(self):
        """Test parsing empty ingredient string."""
        mock_client = Mock()
        mock_client.parse_ingredient.return_value = build_parsed_ingredient(
            input_text="",
            quantity=0.0,
            unit="",
            food=""
        )

        from src.tools import parser
        original_client = parser.MealieClient
        parser.MealieClient = Mock(return_value=mock_client)
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        try:
            result = parser_ingredient("")
            result_dict = json.loads(result)

            assert "ingredient" in result_dict
        finally:
            parser.MealieClient = original_client

    def test_parse_ingredient_api_error(self):
        """Test handling of API error during parsing."""
        from src.client import MealieAPIError

        mock_client = Mock()
        mock_client.parse_ingredient.side_effect = MealieAPIError(
            "Parser error",
            status_code=400,
            response_body="Invalid ingredient format"
        )

        from src.tools import parser
        original_client = parser.MealieClient
        parser.MealieClient = Mock(return_value=mock_client)
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        try:
            result = parser_ingredient("invalid")
            result_dict = json.loads(result)

            assert "error" in result_dict
            assert result_dict["status_code"] == 400
        finally:
            parser.MealieClient = original_client

    def test_parse_ingredient_with_range(self):
        """Test parsing ingredient with quantity range."""
        mock_client = Mock()
        mock_client.parse_ingredient.return_value = build_parsed_ingredient(
            input_text="2-3 cups flour",
            quantity=2.5,  # Parser might average the range
            unit="cup",
            food="flour"
        )

        from src.tools import parser
        original_client = parser.MealieClient
        parser.MealieClient = Mock(return_value=mock_client)
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        try:
            result = parser_ingredient("2-3 cups flour")
            result_dict = json.loads(result)

            assert result_dict["ingredient"]["quantity"] > 0
            assert result_dict["ingredient"]["food"]["name"] == "flour"
        finally:
            parser.MealieClient = original_client


class TestParserIngredientsBatch:
    """Tests for batch ingredient parsing."""

    def test_parse_multiple_ingredients(self):
        """Test parsing a batch of ingredients."""
        mock_client = Mock()
        mock_client.parse_ingredients_batch.return_value = [
            build_parsed_ingredient("2 cups flour", 2.0, "cup", "flour"),
            build_parsed_ingredient("1 tsp salt", 1.0, "teaspoon", "salt"),
            build_parsed_ingredient("1/2 cup butter", 0.5, "cup", "butter")
        ]

        from src.tools import parser
        original_client = parser.MealieClient
        parser.MealieClient = Mock(return_value=mock_client)
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        try:
            ingredients = ["2 cups flour", "1 tsp salt", "1/2 cup butter"]
            result = parser_ingredients_batch(ingredients)
            result_dict = json.loads(result)

            assert "count" in result_dict
            assert "parsed_ingredients" in result_dict
            assert result_dict["count"] == 3
            assert len(result_dict["parsed_ingredients"]) == 3
        finally:
            parser.MealieClient = original_client

    def test_parse_batch_empty_list(self):
        """Test parsing empty ingredient list."""
        mock_client = Mock()
        mock_client.parse_ingredients_batch.return_value = []

        from src.tools import parser
        original_client = parser.MealieClient
        parser.MealieClient = Mock(return_value=mock_client)
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        try:
            result = parser_ingredients_batch([])
            result_dict = json.loads(result)

            assert result_dict["count"] == 0
            assert result_dict["parsed_ingredients"] == []
        finally:
            parser.MealieClient = original_client

    def test_parse_batch_single_ingredient(self):
        """Test batch parsing with single ingredient."""
        mock_client = Mock()
        mock_client.parse_ingredients_batch.return_value = [
            build_parsed_ingredient("2 cups flour", 2.0, "cup", "flour")
        ]

        from src.tools import parser
        original_client = parser.MealieClient
        parser.MealieClient = Mock(return_value=mock_client)
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        try:
            result = parser_ingredients_batch(["2 cups flour"])
            result_dict = json.loads(result)

            assert result_dict["count"] == 1
        finally:
            parser.MealieClient = original_client

    def test_parse_batch_with_different_parser(self):
        """Test batch parsing with alternative parser."""
        mock_client = Mock()
        mock_client.parse_ingredients_batch.return_value = [
            build_parsed_ingredient("2 cups flour", 2.0, "cup", "flour")
        ]

        from src.tools import parser
        original_client = parser.MealieClient
        parser.MealieClient = Mock(return_value=mock_client)
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        try:
            result = parser_ingredients_batch(["2 cups flour"], parser="brute")

            # Verify parser parameter was passed
            mock_client.parse_ingredients_batch.assert_called_once_with(
                ingredients=["2 cups flour"],
                parser="brute"
            )
        finally:
            parser.MealieClient = original_client

    def test_parse_batch_api_error(self):
        """Test handling of API error during batch parsing."""
        from src.client import MealieAPIError

        mock_client = Mock()
        mock_client.parse_ingredients_batch.side_effect = MealieAPIError(
            "Batch parser error",
            status_code=500,
            response_body="Internal server error"
        )

        from src.tools import parser
        original_client = parser.MealieClient
        parser.MealieClient = Mock(return_value=mock_client)
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        try:
            result = parser_ingredients_batch(["2 cups flour"])
            result_dict = json.loads(result)

            assert "error" in result_dict
            assert result_dict["status_code"] == 500
        finally:
            parser.MealieClient = original_client

    def test_parse_batch_mixed_formats(self):
        """Test parsing ingredients with mixed formats."""
        mock_client = Mock()
        mock_client.parse_ingredients_batch.return_value = [
            build_parsed_ingredient("2 cups flour", 2.0, "cup", "flour"),
            build_parsed_ingredient("salt to taste", 0.0, "", "salt"),
            build_parsed_ingredient("3 large eggs", 3.0, "large", "eggs")
        ]

        from src.tools import parser
        original_client = parser.MealieClient
        parser.MealieClient = Mock(return_value=mock_client)
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        try:
            ingredients = ["2 cups flour", "salt to taste", "3 large eggs"]
            result = parser_ingredients_batch(ingredients)
            result_dict = json.loads(result)

            assert result_dict["count"] == 3

            # Verify each ingredient was parsed
            parsed = result_dict["parsed_ingredients"]
            assert parsed[0]["ingredient"]["food"]["name"] == "flour"
            assert parsed[1]["ingredient"]["food"]["name"] == "salt"
            assert parsed[2]["ingredient"]["food"]["name"] == "eggs"
        finally:
            parser.MealieClient = original_client
