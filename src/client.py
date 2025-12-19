"""
Mealie API Client

A robust synchronous HTTP client for interacting with the Mealie API.
Includes error handling, retry logic, and connection testing.
"""

import os
import time
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import httpx
from dotenv import load_dotenv


class MealieAPIError(Exception):
    """Base exception for Mealie API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Optional[str] = None):
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)


class MealieClient:
    """
    Synchronous client for the Mealie API.

    Features:
    - Bearer token authentication
    - Automatic retry with exponential backoff
    - Comprehensive error handling
    - Connection testing

    Environment Variables:
    - MEALIE_URL: Base URL of the Mealie instance (required)
    - MEALIE_API_TOKEN: API token for authentication (required)
    """

    MAX_RETRIES = 3
    RETRY_DELAYS = [1, 2, 4]  # Exponential backoff: 1s, 2s, 4s
    TIMEOUT = 30.0  # seconds

    def __init__(self, base_url: Optional[str] = None, api_token: Optional[str] = None):
        """
        Initialize the Mealie API client.

        Args:
            base_url: Base URL of the Mealie instance (defaults to MEALIE_URL env var)
            api_token: API token for authentication (defaults to MEALIE_API_TOKEN env var)

        Raises:
            ValueError: If required configuration is missing
        """
        self.base_url = base_url or os.getenv("MEALIE_URL")
        self.api_token = api_token or os.getenv("MEALIE_API_TOKEN")

        if not self.base_url:
            raise ValueError("MEALIE_URL must be set in environment or passed to constructor")

        if not self.api_token:
            raise ValueError("MEALIE_API_TOKEN must be set in environment or passed to constructor")

        # Ensure base URL doesn't end with trailing slash
        self.base_url = self.base_url.rstrip("/")

        # Set up HTTP client with auth headers
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Create synchronous HTTP client
        self.client = httpx.Client(
            headers=self.headers,
            timeout=self.TIMEOUT,
            follow_redirects=True,
        )

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close client on context manager exit."""
        self.close()

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def _build_url(self, endpoint: str) -> str:
        """
        Build full URL from endpoint.

        Args:
            endpoint: API endpoint path (e.g., "/api/recipes")

        Returns:
            Full URL
        """
        # Ensure endpoint starts with /
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"

        return urljoin(self.base_url, endpoint)

    def _should_retry(self, exception: Exception, attempt: int) -> bool:
        """
        Determine if request should be retried.

        Args:
            exception: Exception that occurred
            attempt: Current attempt number (0-indexed)

        Returns:
            True if should retry, False otherwise
        """
        if attempt >= self.MAX_RETRIES:
            return False

        # Retry on connection errors
        if isinstance(exception, (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError)):
            return True

        # Retry on 5xx server errors
        if isinstance(exception, httpx.HTTPStatusError):
            return exception.response.status_code >= 500

        return False

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: Query parameters
            data: Form data
            json: JSON body

        Returns:
            Response JSON data

        Raises:
            MealieAPIError: If request fails after retries
        """
        url = self._build_url(endpoint)

        for attempt in range(self.MAX_RETRIES + 1):
            try:
                response = self.client.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    json=json,
                )

                # Raise for 4xx and 5xx status codes
                response.raise_for_status()

                # Return JSON if present, otherwise return None
                if response.content:
                    try:
                        return response.json()
                    except Exception:
                        return response.text
                return None

            except httpx.HTTPStatusError as e:
                # For 4xx errors, don't retry
                if 400 <= e.response.status_code < 500:
                    raise MealieAPIError(
                        f"Client error {e.response.status_code}: {e.response.text}",
                        status_code=e.response.status_code,
                        response_body=e.response.text,
                    )

                # For 5xx errors, retry if attempts remain
                if self._should_retry(e, attempt):
                    delay = self.RETRY_DELAYS[attempt]
                    time.sleep(delay)
                    continue

                raise MealieAPIError(
                    f"Server error {e.response.status_code}: {e.response.text}",
                    status_code=e.response.status_code,
                    response_body=e.response.text,
                )

            except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as e:
                # Retry connection errors
                if self._should_retry(e, attempt):
                    delay = self.RETRY_DELAYS[attempt]
                    time.sleep(delay)
                    continue

                raise MealieAPIError(
                    f"Connection error: {str(e)}",
                )

            except Exception as e:
                raise MealieAPIError(
                    f"Unexpected error: {str(e)}",
                )

        # Should never reach here, but just in case
        raise MealieAPIError("Request failed after maximum retries")

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Perform GET request.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            Response JSON data
        """
        return self._make_request("GET", endpoint, params=params)

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Perform POST request.

        Args:
            endpoint: API endpoint path
            data: Form data
            json: JSON body

        Returns:
            Response JSON data
        """
        return self._make_request("POST", endpoint, data=data, json=json)

    def put(self, endpoint: str, json: Optional[Dict[str, Any]] = None) -> Any:
        """
        Perform PUT request.

        Args:
            endpoint: API endpoint path
            json: JSON body

        Returns:
            Response JSON data
        """
        return self._make_request("PUT", endpoint, json=json)

    def patch(self, endpoint: str, json: Optional[Dict[str, Any]] = None) -> Any:
        """
        Perform PATCH request.

        Args:
            endpoint: API endpoint path
            json: JSON body

        Returns:
            Response JSON data
        """
        return self._make_request("PATCH", endpoint, json=json)

    def delete(self, endpoint: str) -> Any:
        """
        Perform DELETE request.

        Args:
            endpoint: API endpoint path

        Returns:
            Response JSON data
        """
        return self._make_request("DELETE", endpoint)

    def test_connection(self) -> bool:
        """
        Test connection to Mealie instance.

        Calls /api/app/about endpoint to verify connectivity and authentication.

        Returns:
            True if connection successful

        Raises:
            MealieAPIError: If connection fails with details
        """
        try:
            response = self.get("/api/app/about")

            # Verify we got a response
            if response is None:
                raise MealieAPIError("Empty response from /api/app/about")

            # If response is a dict, check for expected fields
            if isinstance(response, dict):
                # Mealie /api/app/about typically returns version info
                if "version" in response or "apiVersion" in response or "versionAPI" in response:
                    return True

                # Response looks valid even without these specific fields
                return True

            # Got some response, consider it successful
            return True

        except MealieAPIError as e:
            # Re-raise with more context
            raise MealieAPIError(
                f"Connection test failed: {str(e)}",
                status_code=e.status_code,
                response_body=e.response_body,
            )

    def parse_ingredient(self, ingredient: str, parser: str = "nlp") -> Dict[str, Any]:
        """
        Parse a single ingredient string to structured format.

        Args:
            ingredient: The ingredient string to parse (e.g., "2 cups flour")
            parser: Parser type - "nlp", "brute", or "openai" (default: "nlp")

        Returns:
            ParsedIngredient dict with input, confidence, and ingredient fields

        Raises:
            MealieAPIError: If parsing fails
        """
        payload = {
            "ingredient": ingredient,
            "parser": parser
        }
        return self.post("/api/parser/ingredient", json=payload)

    def parse_ingredients_batch(self, ingredients: list[str], parser: str = "nlp") -> list[Dict[str, Any]]:
        """
        Parse multiple ingredient strings to structured format.

        Args:
            ingredients: List of ingredient strings to parse
            parser: Parser type - "nlp", "brute", or "openai" (default: "nlp")

        Returns:
            List of ParsedIngredient dicts

        Raises:
            MealieAPIError: If parsing fails
        """
        payload = {
            "ingredients": ingredients,
            "parser": parser
        }
        return self.post("/api/parser/ingredients", json=payload)

    def update_recipe_ingredients(self, slug: str, ingredients: list[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update a recipe with structured ingredients.

        Args:
            slug: The recipe's slug identifier
            ingredients: List of structured ingredient dicts with keys:
                - quantity: number (nullable)
                - unit: dict with id and name, or just name string (nullable)
                - food: dict with id and name, or just name string (nullable)
                - note: string (nullable)
                - display: string for human-readable format

        Returns:
            Updated recipe data

        Raises:
            MealieAPIError: If update fails
        """
        # v1.4.7: Send minimal payload instead of full recipe to trigger proper Pydantic validation
        # PATCH with only the field we want to update
        minimal_payload = {
            "recipeIngredient": ingredients  # API uses camelCase
        }
        return self.patch(f"/api/recipes/{slug}", json=minimal_payload)


if __name__ == "__main__":
    """
    Test the Mealie client against the live instance.
    """
    print("Testing Mealie API Client...")
    print("-" * 50)

    # Load environment variables from .env file
    load_dotenv()

    try:
        # Create client
        print("Creating MealieClient...")
        with MealieClient() as client:
            print(f"Base URL: {client.base_url}")
            print(f"Token: {client.api_token[:20]}..." if client.api_token else "Token: None")
            print()

            # Test connection
            print("Testing connection to Mealie instance...")
            result = client.test_connection()
            print(f"Connection test: {'SUCCESS' if result else 'FAILED'}")
            print()

            # Try to get about info
            print("Fetching /api/app/about...")
            about = client.get("/api/app/about")
            print(f"Response: {about}")
            print()

            print("-" * 50)
            print("All tests passed!")

    except MealieAPIError as e:
        print(f"ERROR: {e}")
        if e.status_code:
            print(f"Status Code: {e.status_code}")
        if e.response_body:
            print(f"Response: {e.response_body}")
        print("-" * 50)
        print("Tests failed!")
        exit(1)

    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        print("-" * 50)
        print("Tests failed!")
        exit(1)
