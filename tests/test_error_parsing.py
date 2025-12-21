"""
Tests for error message parsing functionality.

This module tests the _parse_api_error function and MealieAPIError class
to ensure they properly parse and format error responses from the Mealie API.
"""

import json
import pytest
from src.client import MealieAPIError, _parse_api_error


class TestParseApiError:
    """Test the _parse_api_error function with various error formats."""

    def test_422_validation_error_with_field_details(self):
        """Test parsing FastAPI validation error with field details."""
        response = json.dumps({
            "detail": [
                {
                    "loc": ["body", "name"],
                    "msg": "field required",
                    "type": "value_error.missing"
                },
                {
                    "loc": ["body", "email"],
                    "msg": "invalid email format",
                    "type": "value_error.email"
                }
            ]
        })

        result = _parse_api_error(422, response)

        assert result["message"] == "Validation Error (HTTP 422)"
        assert len(result["details"]) == 2
        assert "Field 'body -> name': field required" in result["details"][0]
        assert "Field 'body -> email': invalid email format" in result["details"][1]
        assert "Check that all required fields are provided" in result["suggestions"]

    def test_422_validation_error_with_single_string(self):
        """Test parsing 422 error with single string detail."""
        response = json.dumps({
            "detail": "Invalid input data"
        })

        result = _parse_api_error(422, response)

        assert result["message"] == "Validation Error (HTTP 422)"
        assert "Invalid input data" in result["details"]
        assert len(result["suggestions"]) > 0

    def test_500_server_error(self):
        """Test parsing 500 server error."""
        response = json.dumps({
            "detail": "Internal server error occurred"
        })

        result = _parse_api_error(500, response)

        assert result["message"] == "Server Error (HTTP 500)"
        assert "Internal server error occurred" in result["details"]
        assert any("kubectl logs" in s for s in result["suggestions"])

    def test_409_conflict_with_known_issue(self):
        """Test parsing 409 conflict error with known issue link."""
        response = json.dumps({
            "detail": "Recipe already exists with this name"
        })

        result = _parse_api_error(409, response)

        assert result["message"] == "Conflict (HTTP 409)"
        assert "Recipe already exists" in result["details"][0]
        # Check for known issue link
        assert any("github.com/mdlopresti/mealie-mcp/issues/7" in s
                  for s in result["suggestions"])

    def test_simple_error_format(self):
        """Test parsing simple error object format."""
        response = json.dumps({
            "error": "Resource not found"
        })

        result = _parse_api_error(404, response)

        assert "Resource not found" in result["details"]

    def test_message_format(self):
        """Test parsing error with message field."""
        response = json.dumps({
            "message": "Authentication failed"
        })

        result = _parse_api_error(401, response)

        assert "Authentication failed" in result["details"]

    def test_non_json_response(self):
        """Test handling non-JSON response."""
        response = "<html>500 Internal Server Error</html>"

        result = _parse_api_error(500, response)

        assert result["message"] == "Server Error (HTTP 500)"
        assert any("Raw error:" in d for d in result["details"])
        assert result["raw_response"] == response

    def test_empty_response(self):
        """Test handling empty response."""
        response = ""

        result = _parse_api_error(500, response)

        assert "Raw error:" in result["details"][0]

    def test_malformed_json(self):
        """Test handling malformed JSON."""
        response = '{"detail": invalid json}'

        result = _parse_api_error(422, response)

        assert any("Raw error:" in d for d in result["details"])

    def test_unexpected_json_structure(self):
        """Test handling unexpected JSON structure."""
        response = json.dumps({
            "unknown_field": "some value",
            "another_field": ["list", "of", "items"]
        })

        result = _parse_api_error(400, response)

        # Should extract something useful
        assert len(result["details"]) > 0
        assert result["raw_response"] == response

    def test_unknown_status_code(self):
        """Test handling unknown status code."""
        response = json.dumps({
            "detail": "Some error"
        })

        result = _parse_api_error(418, response)  # I'm a teapot

        assert result["message"] == "HTTP 418 Error"
        assert "Some error" in result["details"]
        assert result["suggestions"] == []  # No template for 418


class TestMealieAPIError:
    """Test the MealieAPIError exception class."""

    def test_error_with_parsing(self):
        """Test that MealieAPIError uses parsed details."""
        response_body = json.dumps({
            "detail": [
                {
                    "loc": ["body", "slug"],
                    "msg": "field required",
                    "type": "value_error.missing"
                }
            ]
        })

        error = MealieAPIError(
            "Original message",
            status_code=422,
            response_body=response_body
        )

        # Check that parsed_details is set
        assert error.parsed_details is not None
        assert error.parsed_details["message"] == "Validation Error (HTTP 422)"
        assert len(error.parsed_details["details"]) == 1

        # Check that error message was enhanced
        error_str = str(error)
        assert "Validation Error (HTTP 422)" in error_str
        assert "Field 'body -> slug': field required" in error_str
        assert "Suggestions:" in error_str

    def test_error_without_status_code(self):
        """Test MealieAPIError without status code (no parsing)."""
        error = MealieAPIError("Connection timeout")

        assert error.status_code is None
        assert error.response_body is None
        assert error.parsed_details is None
        assert str(error) == "Connection timeout"

    def test_error_without_response_body(self):
        """Test MealieAPIError with status code but no response body."""
        error = MealieAPIError(
            "Server error",
            status_code=500,
            response_body=None
        )

        assert error.status_code == 500
        assert error.response_body is None
        assert error.parsed_details is None
        assert str(error) == "Server error"

    def test_backward_compatibility_attributes(self):
        """Test that all original attributes are preserved."""
        response_body = json.dumps({"detail": "Test error"})

        error = MealieAPIError(
            "Original message",
            status_code=422,
            response_body=response_body
        )

        # All original attributes should still exist
        assert hasattr(error, "status_code")
        assert hasattr(error, "response_body")
        assert error.status_code == 422
        assert error.response_body == response_body

        # New attribute added
        assert hasattr(error, "parsed_details")

    def test_500_error_formatting(self):
        """Test 500 error message formatting."""
        response_body = json.dumps({
            "detail": "Database connection failed"
        })

        error = MealieAPIError(
            "Server error",
            status_code=500,
            response_body=response_body
        )

        error_str = str(error)
        assert "Server Error (HTTP 500)" in error_str
        assert "Database connection failed" in error_str
        assert "kubectl logs" in error_str

    def test_409_error_with_github_link(self):
        """Test 409 error includes GitHub issue link for known problems."""
        response_body = json.dumps({
            "detail": "Recipe already exists"
        })

        error = MealieAPIError(
            "Conflict",
            status_code=409,
            response_body=response_body
        )

        error_str = str(error)
        assert "Conflict (HTTP 409)" in error_str
        assert "github.com/mdlopresti/mealie-mcp/issues/7" in error_str


class TestErrorMessageFormats:
    """Test various real-world error message formats."""

    def test_fastapi_validation_nested_fields(self):
        """Test FastAPI validation error with nested field paths."""
        response = json.dumps({
            "detail": [
                {
                    "loc": ["body", "recipeIngredient", 0, "quantity"],
                    "msg": "value is not a valid float",
                    "type": "type_error.float"
                }
            ]
        })

        result = _parse_api_error(422, response)

        assert "body -> recipeIngredient -> 0 -> quantity" in result["details"][0]
        assert "value is not a valid float" in result["details"][0]

    def test_multiple_error_types(self):
        """Test handling multiple different error types in one response."""
        response = json.dumps({
            "detail": [
                {
                    "loc": ["body", "name"],
                    "msg": "field required",
                    "type": "value_error.missing"
                },
                {
                    "loc": ["body", "prepTime"],
                    "msg": "invalid time format",
                    "type": "value_error"
                },
                {
                    "loc": ["query", "page"],
                    "msg": "value must be greater than 0",
                    "type": "value_error.number.not_gt"
                }
            ]
        })

        result = _parse_api_error(422, response)

        assert len(result["details"]) == 3
        assert all("Field" in d for d in result["details"])

    def test_error_list_with_non_dict_items(self):
        """Test handling error list with non-dict items."""
        response = json.dumps({
            "detail": [
                "First error",
                "Second error",
                {"loc": ["body", "field"], "msg": "structured error", "type": "value_error"}
            ]
        })

        result = _parse_api_error(422, response)

        assert "First error" in result["details"]
        assert "Second error" in result["details"]
        assert "Field 'body -> field': structured error" in result["details"][2]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
