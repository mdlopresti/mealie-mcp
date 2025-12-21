"""
Basic tests for MealieClient initialization and URL building.

Focuses on non-network code paths that don't require mocking.
"""

import pytest
import os
from src.client import MealieClient, MealieAPIError, _parse_api_error
import json


class TestMealieClientInit:
    """Test MealieClient initialization."""

    def test_init_missing_url(self, monkeypatch):
        """Test initialization fails without URL."""
        monkeypatch.delenv("MEALIE_URL", raising=False)
        monkeypatch.setenv("MEALIE_API_TOKEN", "test-token")

        with pytest.raises(ValueError, match="MEALIE_URL"):
            MealieClient()

    def test_init_missing_token(self, monkeypatch):
        """Test initialization fails without token."""
        monkeypatch.setenv("MEALIE_URL", "https://test.example.com")
        monkeypatch.delenv("MEALIE_API_TOKEN", raising=False)

        with pytest.raises(ValueError, match="MEALIE_API_TOKEN"):
            MealieClient()

    def test_init_from_env(self, monkeypatch):
        """Test initialization from environment variables."""
        monkeypatch.setenv("MEALIE_URL", "https://env.example.com")
        monkeypatch.setenv("MEALIE_API_TOKEN", "env-token")

        client = MealieClient()
        assert client.base_url == "https://env.example.com"
        assert client.api_token == "env-token"

    def test_init_explicit_overrides_env(self, monkeypatch):
        """Test explicit parameters override environment."""
        monkeypatch.setenv("MEALIE_URL", "https://env.example.com")
        monkeypatch.setenv("MEALIE_API_TOKEN", "env-token")

        client = MealieClient(
            base_url="https://explicit.example.com",
            api_token="explicit-token"
        )
        assert client.base_url == "https://explicit.example.com"
        assert client.api_token == "explicit-token"

    def test_trailing_slash_removed(self):
        """Test trailing slash is removed from base URL."""
        client = MealieClient(
            base_url="https://test.example.com/",
            api_token="token"
        )
        assert client.base_url == "https://test.example.com"


class TestURLBuilding:
    """Test URL construction."""

    def test_build_url_simple(self):
        """Test building URL with simple endpoint."""
        client = MealieClient(base_url="https://test.example.com", api_token="token")
        url = client._build_url("/api/recipes")
        assert url == "https://test.example.com/api/recipes"

    def test_build_url_without_leading_slash(self):
        """Test URL building without leading slash."""
        client = MealieClient(base_url="https://test.example.com", api_token="token")
        url = client._build_url("api/recipes")
        assert url == "https://test.example.com/api/recipes"

    def test_build_url_with_path_params(self):
        """Test URL building with path parameters."""
        client = MealieClient(base_url="https://test.example.com", api_token="token")
        url = client._build_url("/api/recipes/my-recipe-slug")
        assert url == "https://test.example.com/api/recipes/my-recipe-slug"


class TestContextManager:
    """Test context manager support."""

    def test_context_manager_enter_exit(self):
        """Test client works as context manager."""
        with MealieClient(base_url="https://test.example.com", api_token="token") as client:
            assert client.base_url == "https://test.example.com"
            assert client.client is not None
        # Client should be closed after exit


class TestErrorMessageParsing:
    """Test error message parsing function."""

    def test_parse_422_with_field_details(self):
        """Test parsing 422 error with field details."""
        response = json.dumps({
            "detail": [
                {"loc": ["body", "name"], "msg": "field required", "type": "value_error.missing"},
                {"loc": ["body", "email"], "msg": "invalid email", "type": "value_error.email"}
            ]
        })

        result = _parse_api_error(422, response)

        assert result["message"] == "Validation Error (HTTP 422)"
        assert len(result["details"]) == 2
        assert "Field 'body -> name': field required" in result["details"][0]
        assert "Field 'body -> email': invalid email" in result["details"][1]

    def test_parse_422_string_detail(self):
        """Test parsing 422 with string detail."""
        response = json.dumps({"detail": "Invalid input"})

        result = _parse_api_error(422, response)

        assert result["message"] == "Validation Error (HTTP 422)"
        assert "Invalid input" in result["details"]

    def test_parse_500_error(self):
        """Test parsing 500 server error."""
        response = json.dumps({"detail": "Database error"})

        result = _parse_api_error(500, response)

        assert result["message"] == "Server Error (HTTP 500)"
        assert "Database error" in result["details"]
        assert any("kubectl logs" in s for s in result["suggestions"])

    def test_parse_409_with_recipe_exists(self):
        """Test parsing 409 error includes GitHub link for known issue."""
        response = json.dumps({"detail": "Recipe already exists"})

        result = _parse_api_error(409, response)

        assert result["message"] == "Conflict (HTTP 409)"
        assert "Recipe already exists" in result["details"][0]
        assert any("github.com" in s and "issues/7" in s for s in result["suggestions"])

    def test_parse_404_not_found(self):
        """Test parsing 404 not found error."""
        response = json.dumps({"detail": "Resource not found"})

        result = _parse_api_error(404, response)

        assert result["message"] == "HTTP 404 Error"
        assert "Resource not found" in result["details"]

    def test_parse_non_json_response(self):
        """Test parsing non-JSON error response."""
        response = "<html>500 Server Error</html>"

        result = _parse_api_error(500, response)

        assert result["message"] == "Server Error (HTTP 500)"
        assert result["raw_response"] == response
        assert any("Raw error:" in d for d in result["details"])

    def test_parse_malformed_json(self):
        """Test parsing malformed JSON."""
        response = '{invalid json}'

        result = _parse_api_error(422, response)

        assert "Raw error:" in result["details"][0]

    def test_parse_unknown_status_code(self):
        """Test parsing unknown status code."""
        response = json.dumps({"detail": "Some error"})

        result = _parse_api_error(418, response)  # I'm a teapot

        assert result["message"] == "HTTP 418 Error"
        assert "Some error" in result["details"]
        assert result["suggestions"] == []


class TestMealieAPIError:
    """Test MealieAPIError exception class."""

    def test_error_without_parsing(self):
        """Test error without status code (no parsing)."""
        error = MealieAPIError("Simple error message")

        assert str(error) == "Simple error message"
        assert error.status_code is None
        assert error.response_body is None
        assert error.parsed_details is None

    def test_error_with_parsing(self):
        """Test error with status code and parsing."""
        response_body = json.dumps({
            "detail": [
                {"loc": ["body", "field"], "msg": "required", "type": "value_error"}
            ]
        })

        error = MealieAPIError(
            "Original message",
            status_code=422,
            response_body=response_body
        )

        assert error.status_code == 422
        assert error.response_body == response_body
        assert error.parsed_details is not None
        assert "Validation Error" in str(error)

    def test_error_preserves_attributes(self):
        """Test all original attributes are preserved."""
        response = json.dumps({"detail": "test"})

        error = MealieAPIError("msg", status_code=422, response_body=response)

        assert hasattr(error, "status_code")
        assert hasattr(error, "response_body")
        assert hasattr(error, "parsed_details")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
