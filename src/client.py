"""
Mealie API Client

A robust synchronous HTTP client for interacting with the Mealie API.
Includes error handling, retry logic, and connection testing.
"""

import json
import os
import time
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import httpx
from dotenv import load_dotenv


# Error message templates for common status codes
_ERROR_TEMPLATES = {
    422: {
        "title": "Validation Error",
        "suggestions": [
            "Check that all required fields are provided",
            "Verify field values match expected types and formats",
            "Review the error details below for specific field issues"
        ]
    },
    500: {
        "title": "Server Error",
        "suggestions": [
            "The Mealie server encountered an internal error",
            "This may be a bug in Mealie - check server logs: kubectl logs -f <pod-name> -n mealie",
            "Try the operation again, or simplify the request if possible"
        ]
    },
    409: {
        "title": "Conflict",
        "suggestions": [
            "A resource with this name or identifier may already exist",
            "Try using a different name or identifier",
            "Use update/patch operations instead of create for existing resources"
        ],
        "known_issues": {
            "Recipe already exists": "https://github.com/mdlopresti/mealie-mcp/issues/7"
        }
    }
}


def _parse_api_error(status_code: int, response_text: str) -> Dict[str, Any]:
    """
    Parse API error response into human-readable format.

    Args:
        status_code: HTTP status code
        response_text: Raw response body text

    Returns:
        Dict with parsed error details:
        - message: Human-readable error message
        - details: Extracted error details (field names, validation info, etc.)
        - suggestions: List of actionable suggestions
        - raw_response: Original response text (for debugging)
    """
    result = {
        "message": f"HTTP {status_code} Error",
        "details": [],
        "suggestions": [],
        "raw_response": response_text
    }

    # Get template for this status code
    template = _ERROR_TEMPLATES.get(status_code, {})
    if template:
        result["message"] = f"{template.get('title', 'Error')} (HTTP {status_code})"
        result["suggestions"] = template.get("suggestions", [])

    # Try to parse JSON response
    try:
        error_data = json.loads(response_text)
    except (json.JSONDecodeError, ValueError):
        # Non-JSON response - return raw text
        result["details"].append(f"Raw error: {response_text[:200]}")
        return result

    # Handle different error response formats

    # Format 1: FastAPI validation error (422)
    # {"detail": [{"loc": ["body", "field"], "msg": "...", "type": "..."}]}
    if isinstance(error_data, dict) and "detail" in error_data:
        detail = error_data["detail"]

        if isinstance(detail, list):
            # Multiple validation errors
            for err in detail:
                if isinstance(err, dict):
                    # Extract field path
                    field_path = " -> ".join(str(x) for x in err.get("loc", []))
                    msg = err.get("msg", "validation error")
                    err_type = err.get("type", "unknown")

                    result["details"].append(f"Field '{field_path}': {msg} (type: {err_type})")
                else:
                    result["details"].append(str(err))
        elif isinstance(detail, str):
            # Single error message
            result["details"].append(detail)

            # Check for known issues
            for known_msg, issue_url in template.get("known_issues", {}).items():
                if known_msg.lower() in detail.lower():
                    result["suggestions"].append(f"Known issue: {issue_url}")
        else:
            result["details"].append(f"Unexpected detail format: {detail}")

    # Format 2: Simple error object
    # {"error": "message"}
    elif isinstance(error_data, dict) and "error" in error_data:
        result["details"].append(error_data["error"])

    # Format 3: Message field
    # {"message": "error message"}
    elif isinstance(error_data, dict) and "message" in error_data:
        result["details"].append(error_data["message"])

    # Format 4: Unknown structure - dump what we can
    else:
        # Try to extract any useful strings
        if isinstance(error_data, dict):
            for key, value in error_data.items():
                if isinstance(value, str):
                    result["details"].append(f"{key}: {value}")
                elif isinstance(value, list):
                    result["details"].append(f"{key}: {', '.join(str(x) for x in value[:3])}")
        else:
            result["details"].append(f"Unexpected error format: {str(error_data)[:200]}")

    return result


class MealieAPIError(Exception):
    """Base exception for Mealie API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Optional[str] = None):
        self.status_code = status_code
        self.response_body = response_body

        # Parse error response for better messages
        self.parsed_details = None
        if status_code and response_body:
            self.parsed_details = _parse_api_error(status_code, response_body)

            # Build enhanced message
            if self.parsed_details:
                parts = [self.parsed_details["message"]]

                # Add details
                if self.parsed_details["details"]:
                    parts.append("\nDetails:")
                    for detail in self.parsed_details["details"]:
                        parts.append(f"  - {detail}")

                # Add suggestions
                if self.parsed_details["suggestions"]:
                    parts.append("\nSuggestions:")
                    for suggestion in self.parsed_details["suggestions"]:
                        parts.append(f"  - {suggestion}")

                message = "\n".join(parts)

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
                    except Exception as json_err:
                        # Log the JSON parse error for debugging
                        raise MealieAPIError(
                            f"Failed to parse JSON response: {str(json_err)}. Response text: {response.text[:200]}",
                            status_code=response.status_code,
                            response_body=response.text,
                        )
                return None

            except httpx.HTTPStatusError as e:
                # For 4xx errors, don't retry
                if 400 <= e.response.status_code < 500:
                    # MealieAPIError will parse the response and create a helpful message
                    raise MealieAPIError(
                        f"HTTP {e.response.status_code} error",
                        status_code=e.response.status_code,
                        response_body=e.response.text,
                    )

                # For 5xx errors, retry if attempts remain
                if self._should_retry(e, attempt):
                    delay = self.RETRY_DELAYS[attempt]
                    time.sleep(delay)
                    continue

                # Final 5xx error after all retries
                raise MealieAPIError(
                    f"HTTP {e.response.status_code} error",
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

    def create_food(
        self,
        name: str,
        description: Optional[str] = None,
        label_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new food item.

        Args:
            name: The food name
            description: Optional description
            label_id: Optional label ID (UUID) to assign

        Returns:
            Created food data with id

        Raises:
            MealieAPIError: If creation fails
        """
        payload = {"name": name}
        if description is not None:
            payload["description"] = description
        if label_id is not None:
            payload["labelId"] = label_id
        return self.post("/api/foods", json=payload)

    def create_unit(self, name: str) -> Dict[str, Any]:
        """
        Create a new measurement unit.

        Args:
            name: The unit name

        Returns:
            Created unit data with id

        Raises:
            MealieAPIError: If creation fails
        """
        payload = {"name": name}
        return self.post("/api/units", json=payload)

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
        # v1.4.14: Use PATCH with only recipeIngredient field
        # Avoids SQLAlchemy auto_init issues with full recipe PUT
        payload = {"recipeIngredient": ingredients}

        # DEBUG: Print the exact JSON being sent to Mealie
        import sys, json
        print(f"\n=== DEBUG: JSON being sent to Mealie PATCH /api/recipes/{slug} ===", file=sys.stderr)
        print(json.dumps(payload, indent=2), file=sys.stderr)
        print(f"=== END DEBUG ===\n", file=sys.stderr)

        return self.patch(f"/api/recipes/{slug}", json=payload)

    def duplicate_recipe(self, slug: str, new_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Duplicate an existing recipe.

        Args:
            slug: The recipe's slug identifier to duplicate
            new_name: Optional new name for the duplicated recipe (defaults to "Copy of {original_name}")

        Returns:
            The newly created recipe data

        Raises:
            MealieAPIError: If duplication fails
        """
        payload = {}
        if new_name:
            payload["name"] = new_name

        return self.post(f"/api/recipes/{slug}/duplicate", json=payload if payload else None)

    def update_recipe_last_made(self, slug: str, timestamp: Optional[str] = None) -> Dict[str, Any]:
        """
        Update the last made timestamp for a recipe.

        Args:
            slug: The recipe's slug identifier
            timestamp: Optional ISO 8601 timestamp (defaults to current time on server)

        Returns:
            Updated recipe data

        Raises:
            MealieAPIError: If update fails
        """
        payload = {}
        if timestamp:
            payload["timestamp"] = timestamp

        return self.patch(f"/api/recipes/{slug}/last-made", json=payload if payload else None)

    def create_recipes_from_urls_bulk(self, urls: list[str], include_tags: bool = False) -> Dict[str, Any]:
        """
        Import multiple recipes from URLs at once.

        Args:
            urls: List of recipe URLs to import
            include_tags: Whether to include tags from scraped recipes (default False)

        Returns:
            Import results with status for each URL

        Raises:
            MealieAPIError: If import fails
        """
        payload = {
            "urls": urls,
            "include_tags": include_tags
        }

        return self.post("/api/recipes/create/url/bulk", json=payload)

    def bulk_tag_recipes(self, recipe_ids: list[str], tags: list[str]) -> Dict[str, Any]:
        """
        Add tags to multiple recipes at once.

        Args:
            recipe_ids: List of recipe IDs to tag
            tags: List of tag names to add

        Returns:
            Bulk action results

        Raises:
            MealieAPIError: If bulk action fails
        """
        # Convert recipe IDs to slugs (API requires slugs, not IDs)
        recipe_slugs = []
        for recipe_id in recipe_ids:
            recipe = self.get(f"/api/recipes/{recipe_id}")
            recipe_slugs.append(recipe["slug"])

        # Get all existing tags to look up IDs
        all_tags_response = self.list_tags()
        # Handle paginated response
        all_tags = all_tags_response.get("items", all_tags_response) if isinstance(all_tags_response, dict) else all_tags_response
        tag_map = {tag["name"]: tag for tag in all_tags}

        # Convert tag names to tag objects (with id, name, slug)
        # Create missing tags first
        tag_objects = []
        for tag_name in tags:
            if tag_name in tag_map:
                # Use existing tag
                tag_objects.append(tag_map[tag_name])
            else:
                # Tag doesn't exist - create it first
                new_tag = self.create_tag(tag_name)
                tag_objects.append(new_tag)

        payload = {
            "recipes": recipe_slugs,  # Use slugs instead of IDs
            "tags": tag_objects
        }

        return self.post("/api/recipes/bulk-actions/tag", json=payload)

    def bulk_categorize_recipes(self, recipe_ids: list[str], categories: list[str]) -> Dict[str, Any]:
        """
        Add categories to multiple recipes at once.

        Args:
            recipe_ids: List of recipe IDs to categorize
            categories: List of category names to add

        Returns:
            Bulk action results

        Raises:
            MealieAPIError: If bulk action fails
        """
        # Convert recipe IDs to slugs (API requires slugs, not IDs)
        recipe_slugs = []
        for recipe_id in recipe_ids:
            recipe = self.get(f"/api/recipes/{recipe_id}")
            recipe_slugs.append(recipe["slug"])

        # Get all existing categories to look up IDs
        all_categories_response = self.list_categories()
        # Handle paginated response
        all_categories = all_categories_response.get("items", all_categories_response) if isinstance(all_categories_response, dict) else all_categories_response
        category_map = {cat["name"]: cat for cat in all_categories}

        # Convert category names to category objects (with id, name, slug)
        # Create missing categories first
        category_objects = []
        for cat_name in categories:
            if cat_name in category_map:
                # Use existing category
                category_objects.append(category_map[cat_name])
            else:
                # Category doesn't exist - create it first
                new_category = self.create_category(cat_name)
                category_objects.append(new_category)

        payload = {
            "recipes": recipe_slugs,  # Use slugs instead of IDs
            "categories": category_objects
        }

        return self.post("/api/recipes/bulk-actions/categorize", json=payload)

    def bulk_delete_recipes(self, recipe_ids: list[str]) -> Dict[str, Any]:
        """
        Delete multiple recipes at once.

        Args:
            recipe_ids: List of recipe IDs to delete

        Returns:
            Bulk action results

        Raises:
            MealieAPIError: If bulk action fails
        """
        payload = {
            "recipes": recipe_ids
        }

        return self.post("/api/recipes/bulk-actions/delete", json=payload)

    def bulk_export_recipes(self, recipe_ids: list[str], export_format: str = "json") -> Any:
        """
        Export multiple recipes at once.

        Args:
            recipe_ids: List of recipe IDs to export
            export_format: Export format (json, zip, etc.)

        Returns:
            Export data or file

        Raises:
            MealieAPIError: If bulk action fails
        """
        payload = {
            "recipes": recipe_ids,
            "format": export_format
        }

        return self.post("/api/recipes/bulk-actions/export", json=payload)

    def bulk_update_settings(self, recipe_ids: list[str], settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update settings for multiple recipes at once.

        Args:
            recipe_ids: List of recipe IDs to update
            settings: Settings to update (e.g., {"public": true, "show_nutrition": false})

        Returns:
            Bulk action results

        Raises:
            MealieAPIError: If bulk action fails
        """
        payload = {
            "recipes": recipe_ids,
            "settings": settings
        }

        return self.post("/api/recipes/bulk-actions/settings", json=payload)

    # -------------------------------------------------------------------------
    # Meal Plan Rules
    # -------------------------------------------------------------------------

    def list_mealplan_rules(self) -> list[Dict[str, Any]]:
        """List all meal plan rules."""
        return self.get("/api/households/mealplans/rules")

    def get_mealplan_rule(self, rule_id: str) -> Dict[str, Any]:
        """Get a specific meal plan rule by ID."""
        return self.get(f"/api/households/mealplans/rules/{rule_id}")

    def create_mealplan_rule(
        self,
        name: str,
        entry_type: str,
        tags: Optional[list[str]] = None,
        categories: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new meal plan rule."""
        payload = {
            "name": name,
            "entryType": entry_type,
            "tags": tags or [],
            "categories": categories or []
        }
        return self.post("/api/households/mealplans/rules", json=payload)

    def update_mealplan_rule(
        self,
        rule_id: str,
        name: Optional[str] = None,
        entry_type: Optional[str] = None,
        tags: Optional[list[str]] = None,
        categories: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        """Update an existing meal plan rule."""
        payload = {}
        if name is not None:
            payload["name"] = name
        if entry_type is not None:
            payload["entryType"] = entry_type
        if tags is not None:
            payload["tags"] = tags
        if categories is not None:
            payload["categories"] = categories

        return self.patch(f"/api/households/mealplans/rules/{rule_id}", json=payload)

    def delete_mealplan_rule(self, rule_id: str) -> None:
        """Delete a meal plan rule."""
        return self.delete(f"/api/households/mealplans/rules/{rule_id}")

    # -------------------------------------------------------------------------
    # Shopping List Recipe Operations
    # -------------------------------------------------------------------------

    def delete_recipe_from_shopping_list(self, item_id: str, recipe_id: str) -> Dict[str, Any]:
        """Remove recipe ingredients from shopping list."""
        return self.post(f"/api/households/shopping/lists/{item_id}/recipe/{recipe_id}/delete")

    # -------------------------------------------------------------------------
    # Foods & Units Management
    # -------------------------------------------------------------------------

    def list_foods(self, page: int = 1, per_page: int = 50) -> Dict[str, Any]:
        """List all foods with pagination."""
        params = {"page": page, "perPage": per_page}
        return self.get("/api/foods", params=params)

    def get_food(self, food_id: str) -> Dict[str, Any]:
        """Get a specific food by ID."""
        return self.get(f"/api/foods/{food_id}")

    def update_food(
        self,
        food_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        label_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update an existing food.

        Args:
            food_id: The food's ID
            name: New name for the food
            description: New description
            label_id: New label ID (UUID) to assign to the food

        Returns:
            Updated food object

        Note:
            The Mealie API requires PUT with the full food object.
            This method fetches the current food first, then updates it.
        """
        # GET current food to preserve all fields
        current_food = self.get(f"/api/foods/{food_id}")

        # Update only the provided fields
        if name is not None:
            current_food["name"] = name
        if description is not None:
            current_food["description"] = description
        if label_id is not None:
            current_food["labelId"] = label_id

        # PUT the complete updated object
        return self.put(f"/api/foods/{food_id}", json=current_food)

    def delete_food(self, food_id: str) -> None:
        """Delete a food."""
        return self.delete(f"/api/foods/{food_id}")

    def merge_foods(self, from_food_id: str, to_food_id: str) -> Dict[str, Any]:
        """Merge one food into another."""
        payload = {
            "fromFood": from_food_id,
            "toFood": to_food_id
        }
        return self.post("/api/foods/merge", json=payload)

    def list_units(self, page: int = 1, per_page: int = 50) -> Dict[str, Any]:
        """List all units with pagination."""
        params = {"page": page, "perPage": per_page}
        return self.get("/api/units", params=params)

    def get_unit(self, unit_id: str) -> Dict[str, Any]:
        """Get a specific unit by ID."""
        return self.get(f"/api/units/{unit_id}")

    def update_unit(
        self,
        unit_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        abbreviation: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update an existing unit."""
        payload = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if abbreviation is not None:
            payload["abbreviation"] = abbreviation

        return self.patch(f"/api/units/{unit_id}", json=payload)

    def delete_unit(self, unit_id: str) -> None:
        """Delete a unit."""
        return self.delete(f"/api/units/{unit_id}")

    def merge_units(self, from_unit_id: str, to_unit_id: str) -> Dict[str, Any]:
        """Merge one unit into another."""
        payload = {
            "fromUnit": from_unit_id,
            "toUnit": to_unit_id
        }
        return self.post("/api/units/merge", json=payload)

    # -------------------------------------------------------------------------
    # Recipe Image Upload
    # -------------------------------------------------------------------------

    def upload_recipe_image_from_url(self, slug: str, image_url: str) -> Dict[str, Any]:
        """
        Upload an image to an existing recipe from a URL.

        Args:
            slug: Recipe slug
            image_url: URL of the image to download and upload

        Returns:
            Update confirmation

        Raises:
            MealieAPIError: If image download or upload fails
        """
        import io
        from pathlib import Path

        # Download the image
        try:
            response = httpx.get(image_url, timeout=30.0, follow_redirects=True)
            response.raise_for_status()
            image_data = response.content
        except Exception as e:
            raise MealieAPIError(f"Failed to download image from {image_url}: {str(e)}")

        # Determine extension from URL or content-type
        extension = Path(image_url).suffix.lstrip('.').lower()
        if not extension:
            content_type = response.headers.get('content-type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                extension = 'jpg'
            elif 'png' in content_type:
                extension = 'png'
            elif 'webp' in content_type:
                extension = 'webp'
            else:
                extension = 'jpg'  # default fallback

        # Upload to Mealie using multipart/form-data
        # Both image (file) and extension (text) go in the files dict
        files = {
            'image': (f'image.{extension}', io.BytesIO(image_data), f'image/{extension}'),
            'extension': (None, extension)  # Text field in multipart, no filename
        }

        endpoint = f"/api/recipes/{slug}/image"
        url = urljoin(self.base_url, endpoint)

        # Debug logging
        import sys
        print(f"DEBUG: Uploading image to {url}", file=sys.stderr)
        print(f"DEBUG: Extension={extension}, Image size={len(image_data)} bytes", file=sys.stderr)

        try:
            # Use standalone httpx.put() to avoid client's default Content-Type header
            # httpx will automatically set Content-Type: multipart/form-data with boundary
            headers = {"Authorization": f"Bearer {self.api_token}"}

            resp = httpx.put(
                url,
                files=files,
                headers=headers,
                timeout=self.TIMEOUT,
                follow_redirects=True
            )
            print(f"DEBUG: Response status={resp.status_code}", file=sys.stderr)
            resp.raise_for_status()
            return {"success": True, "message": f"Image uploaded to recipe '{slug}'"}
        except httpx.HTTPStatusError as e:
            raise MealieAPIError(
                f"Failed to upload image to recipe: {e.response.text}",
                status_code=e.response.status_code,
                response_body=e.response.text
            )
        except Exception as e:
            raise MealieAPIError(f"Failed to upload image: {str(e)}")

    # -------------------------------------------------------------------------
    # Recipe from Image
    # -------------------------------------------------------------------------

    def create_recipe_from_image(self, image_data: str, extension: str = "jpg") -> Dict[str, Any]:
        """
        Create recipe from image using AI (experimental).

        Args:
            image_data: Base64 encoded image data
            extension: Image file extension (jpg, png, etc.)

        Returns:
            Created recipe data
        """
        payload = {
            "image": image_data,
            "extension": extension
        }
        return self.post("/api/recipes/create/image", json=payload)

    # -------------------------------------------------------------------------
    # Organizers Management (Categories, Tags, Tools)
    # -------------------------------------------------------------------------

    def list_categories(self) -> list[Dict[str, Any]]:
        """List all categories."""
        return self.get("/api/organizers/categories")

    def list_tags(self) -> list[Dict[str, Any]]:
        """List all tags."""
        return self.get("/api/organizers/tags")

    def list_tools(self) -> list[Dict[str, Any]]:
        """List all tools."""
        return self.get("/api/organizers/tools")

    def create_category(self, name: str) -> Dict[str, Any]:
        """Create a new category."""
        return self.post("/api/organizers/categories", json={"name": name})

    def get_category(self, category_id: str) -> Dict[str, Any]:
        """Get a category by ID."""
        return self.get(f"/api/organizers/categories/{category_id}")

    def create_tag(self, name: str) -> Dict[str, Any]:
        """Create a new tag."""
        return self.post("/api/organizers/tags", json={"name": name})

    def get_tag(self, tag_id: str) -> Dict[str, Any]:
        """Get a tag by ID."""
        return self.get(f"/api/organizers/tags/{tag_id}")

    def create_tool(self, name: str) -> Dict[str, Any]:
        """Create a new kitchen tool."""
        return self.post("/api/organizers/tools", json={"name": name})

    def get_tool(self, tool_id: str) -> Dict[str, Any]:
        """Get a kitchen tool by ID."""
        return self.get(f"/api/organizers/tools/{tool_id}")

    def update_category(
        self,
        category_id: str,
        name: Optional[str] = None,
        slug: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a category."""
        payload = {}
        if name is not None:
            payload["name"] = name
        if slug is not None:
            payload["slug"] = slug

        return self.patch(f"/api/organizers/categories/{category_id}", json=payload)

    def delete_category(self, category_id: str) -> None:
        """Delete a category."""
        return self.delete(f"/api/organizers/categories/{category_id}")

    def update_tag(
        self,
        tag_id: str,
        name: Optional[str] = None,
        slug: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a tag."""
        payload = {}
        if name is not None:
            payload["name"] = name
        if slug is not None:
            payload["slug"] = slug

        return self.patch(f"/api/organizers/tags/{tag_id}", json=payload)

    def delete_tag(self, tag_id: str) -> None:
        """Delete a tag."""
        return self.delete(f"/api/organizers/tags/{tag_id}")

    def update_tool(
        self,
        tool_id: str,
        name: Optional[str] = None,
        slug: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a tool."""
        payload = {}
        if name is not None:
            payload["name"] = name
        if slug is not None:
            payload["slug"] = slug

        return self.patch(f"/api/organizers/tools/{tool_id}", json=payload)

    def delete_tool(self, tool_id: str) -> None:
        """Delete a tool."""
        return self.delete(f"/api/organizers/tools/{tool_id}")


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
