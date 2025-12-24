"""Mock client factories for creating configured MealieClient mocks.

This module provides utilities for creating MealieClient mocks with pre-configured
responses. Supports both simple quick creation and complex builder pattern.

Usage - Simple:
    >>> mock = create_mock_client(get_value={"id": "123"})
    >>> with patch('src.tools.recipes.MealieClient', return_value=mock):
    ...     result = recipes_get("test-slug")

Usage - Builder Pattern:
    >>> mock = (MockClientBuilder()
    ...     .with_recipe_responses()
    ...     .with_error_on_method("delete", 404, "Not Found")
    ...     .build())

Usage - Pre-configured Scenarios:
    >>> mock = MockResponsePresets.recipe_crud()
    >>> mock = MockResponsePresets.mealplan_workflow()
"""

from unittest.mock import MagicMock
from typing import Any, Dict, List, Optional, Callable
from src.client import MealieAPIError


def create_mock_client(
    get_value: Any = None,
    post_value: Any = None,
    patch_value: Any = None,
    put_value: Any = None,
    delete_value: Any = None,
    get_side_effect: Optional[Callable] = None,
    post_side_effect: Optional[Callable] = None,
    patch_side_effect: Optional[Callable] = None,
    put_side_effect: Optional[Callable] = None,
    delete_side_effect: Optional[Callable] = None,
) -> MagicMock:
    """Create a mock MealieClient with configured return values.

    Enhanced version of the pattern used in existing tests. Supports both
    return values and side effects for all HTTP methods.

    Args:
        get_value: Return value for GET requests
        post_value: Return value for POST requests
        patch_value: Return value for PATCH requests
        put_value: Return value for PUT requests
        delete_value: Return value for DELETE requests
        get_side_effect: Side effect function for GET (overrides get_value)
        post_side_effect: Side effect function for POST (overrides post_value)
        patch_side_effect: Side effect function for PATCH (overrides patch_value)
        put_side_effect: Side effect function for PUT (overrides put_value)
        delete_side_effect: Side effect function for DELETE (overrides delete_value)

    Returns:
        Configured MagicMock that can be used as a MealieClient

    Example - Simple returns:
        >>> mock = create_mock_client(get_value={"id": "123", "name": "Test"})
        >>> result = mock.get("/api/recipes/test")
        >>> assert result["name"] == "Test"

    Example - Multiple methods:
        >>> mock = create_mock_client(
        ...     get_value={"id": "123"},
        ...     post_value={"id": "456", "name": "Created"},
        ...     delete_value=None
        ... )

    Example - Side effects for dynamic behavior:
        >>> def get_recipe(path):
        ...     if "test" in path:
        ...         return {"id": "123", "name": "Test"}
        ...     return {"id": "456", "name": "Other"}
        >>> mock = create_mock_client(get_side_effect=get_recipe)
    """
    mock = MagicMock()
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=None)

    # Configure GET
    if get_side_effect is not None:
        mock.get.side_effect = get_side_effect
    elif get_value is not None:
        mock.get.return_value = get_value

    # Configure POST
    if post_side_effect is not None:
        mock.post.side_effect = post_side_effect
    elif post_value is not None:
        mock.post.return_value = post_value

    # Configure PATCH
    if patch_side_effect is not None:
        mock.patch.side_effect = patch_side_effect
    elif patch_value is not None:
        mock.patch.return_value = patch_value

    # Configure PUT
    if put_side_effect is not None:
        mock.put.side_effect = put_side_effect
    elif put_value is not None:
        mock.put.return_value = put_value

    # Configure DELETE
    if delete_side_effect is not None:
        mock.delete.side_effect = delete_side_effect
    elif delete_value is not None:
        mock.delete.return_value = delete_value

    return mock


class MockClientBuilder:
    """Builder for creating complex mock clients with pre-configured scenarios.

    Provides a fluent API for building mock clients with realistic responses
    for common workflows.

    Example:
        >>> mock = (MockClientBuilder()
        ...     .with_recipe_responses()
        ...     .with_pagination(total=100, per_page=20)
        ...     .with_error_on_delete()
        ...     .build())
    """

    def __init__(self):
        """Initialize builder with empty configuration."""
        self._get_responses: Dict[str, Any] = {}
        self._post_responses: Dict[str, Any] = {}
        self._patch_responses: Dict[str, Any] = {}
        self._put_responses: Dict[str, Any] = {}
        self._delete_responses: Dict[str, Any] = {}
        self._errors: Dict[str, MealieAPIError] = {}

    def with_get_response(self, path_pattern: str, response: Any) -> "MockClientBuilder":
        """Configure GET response for specific path pattern.

        Args:
            path_pattern: Path pattern to match (substring)
            response: Response data to return

        Returns:
            Self for chaining
        """
        self._get_responses[path_pattern] = response
        return self

    def with_post_response(self, path_pattern: str, response: Any) -> "MockClientBuilder":
        """Configure POST response for specific path pattern."""
        self._post_responses[path_pattern] = response
        return self

    def with_patch_response(self, path_pattern: str, response: Any) -> "MockClientBuilder":
        """Configure PATCH response for specific path pattern."""
        self._patch_responses[path_pattern] = response
        return self

    def with_put_response(self, path_pattern: str, response: Any) -> "MockClientBuilder":
        """Configure PUT response for specific path pattern."""
        self._put_responses[path_pattern] = response
        return self

    def with_delete_response(self, path_pattern: str, response: Any) -> "MockClientBuilder":
        """Configure DELETE response for specific path pattern."""
        self._delete_responses[path_pattern] = response
        return self

    def with_error_on_method(
        self,
        method: str,
        status_code: int = 500,
        message: str = "Server Error",
        response_body: str = ""
    ) -> "MockClientBuilder":
        """Configure an error to be raised on a specific HTTP method.

        Args:
            method: HTTP method (get, post, patch, put, delete)
            status_code: HTTP status code for error
            message: Error message
            response_body: Response body text

        Returns:
            Self for chaining

        Example:
            >>> builder.with_error_on_method("delete", 404, "Not Found")
        """
        self._errors[method.lower()] = MealieAPIError(
            message, status_code=status_code, response_body=response_body
        )
        return self

    def with_recipe_responses(self) -> "MockClientBuilder":
        """Configure common recipe CRUD responses.

        Sets up typical responses for:
        - GET /api/recipes/{slug} - Returns sample recipe
        - POST /api/recipes - Returns created recipe
        - PATCH /api/recipes/{slug} - Returns updated recipe
        - DELETE /api/recipes/{slug} - Returns None

        Returns:
            Self for chaining
        """
        sample_recipe = {
            "id": "recipe-123",
            "slug": "test-recipe",
            "name": "Test Recipe",
            "description": "A test recipe",
            "recipeIngredient": ["2 cups flour", "1 tsp salt"],
            "recipeInstructions": [{"text": "Mix and bake"}],
        }

        self._get_responses["/recipes/"] = sample_recipe
        self._post_responses["/recipes"] = sample_recipe
        self._patch_responses["/recipes/"] = sample_recipe
        self._delete_responses["/recipes/"] = None
        return self

    def with_mealplan_responses(self) -> "MockClientBuilder":
        """Configure common meal plan responses."""
        sample_mealplan = {
            "id": "mealplan-123",
            "date": "2025-12-25",
            "entryType": "dinner",
            "title": "Test Meal",
            "recipeId": None,
            "groupId": "group-123",
            "userId": "user-123",
        }

        self._get_responses["/mealplans/"] = sample_mealplan
        self._post_responses["/mealplans"] = sample_mealplan
        self._put_responses["/mealplans/"] = sample_mealplan
        self._delete_responses["/mealplans/"] = None
        return self

    def with_shopping_list_responses(self) -> "MockClientBuilder":
        """Configure common shopping list responses."""
        sample_list = {
            "id": "list-123",
            "name": "Test Shopping List",
            "listItems": [],
            "groupId": "group-123",
        }

        self._get_responses["/shopping/lists/"] = sample_list
        self._post_responses["/shopping/lists"] = sample_list
        self._patch_responses["/shopping/lists/"] = sample_list
        self._delete_responses["/shopping/lists/"] = None
        return self

    def with_pagination(
        self,
        items: List[Any] = None,
        page: int = 1,
        per_page: int = 20,
        total: int = None
    ) -> "MockClientBuilder":
        """Configure paginated list response.

        Args:
            items: List of items to return (uses sample data if None)
            page: Current page number
            per_page: Items per page
            total: Total number of items

        Returns:
            Self for chaining

        Example:
            >>> builder.with_pagination(items=[recipe1, recipe2], total=100)
        """
        if items is None:
            items = [{"id": f"item-{i}"} for i in range(per_page)]

        if total is None:
            total = len(items)

        response = {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page,
            "items": items,
        }

        # Add to GET responses for list endpoints
        self._get_responses["default_list"] = response
        return self

    def build(self) -> MagicMock:
        """Build the configured mock client.

        Returns:
            Configured MagicMock ready to use as MealieClient

        Example:
            >>> mock = builder.build()
            >>> with patch('src.tools.recipes.MealieClient', return_value=mock):
            ...     # Use in tests
        """
        def make_side_effect(responses: Dict[str, Any], method: str):
            """Create side effect function that matches path patterns."""
            def side_effect(path, *args, **kwargs):
                # Check for method-level error
                if method in self._errors:
                    raise self._errors[method]

                # Try to match path pattern
                for pattern, response in responses.items():
                    if pattern in path or pattern == "default_list":
                        return response

                # Default: return empty dict
                return {}

            return side_effect

        return create_mock_client(
            get_side_effect=make_side_effect(self._get_responses, "get") if self._get_responses else None,
            post_side_effect=make_side_effect(self._post_responses, "post") if self._post_responses else None,
            patch_side_effect=make_side_effect(self._patch_responses, "patch") if self._patch_responses else None,
            put_side_effect=make_side_effect(self._put_responses, "put") if self._put_responses else None,
            delete_side_effect=make_side_effect(self._delete_responses, "delete") if self._delete_responses else None,
        )


class MockResponsePresets:
    """Pre-configured mock clients for common test scenarios.

    Provides ready-to-use mock clients for typical workflows, reducing
    boilerplate in tests.

    Example:
        >>> mock = MockResponsePresets.recipe_crud()
        >>> mock = MockResponsePresets.mealplan_workflow()
    """

    @staticmethod
    def recipe_crud() -> MagicMock:
        """Mock client configured for recipe CRUD operations.

        Returns:
            Mock client with recipe responses configured
        """
        return MockClientBuilder().with_recipe_responses().build()

    @staticmethod
    def mealplan_workflow() -> MagicMock:
        """Mock client configured for meal planning workflow.

        Returns:
            Mock client with meal plan and recipe responses
        """
        return (
            MockClientBuilder()
            .with_recipe_responses()
            .with_mealplan_responses()
            .build()
        )

    @staticmethod
    def shopping_workflow() -> MagicMock:
        """Mock client configured for shopping list workflow.

        Returns:
            Mock client with shopping list, recipe, and meal plan responses
        """
        return (
            MockClientBuilder()
            .with_recipe_responses()
            .with_mealplan_responses()
            .with_shopping_list_responses()
            .build()
        )

    @staticmethod
    def error_scenarios() -> MagicMock:
        """Mock client configured to simulate various error conditions.

        Returns:
            Mock client that raises errors on all methods
        """
        return (
            MockClientBuilder()
            .with_error_on_method("get", 404, "Not Found")
            .with_error_on_method("post", 400, "Bad Request")
            .with_error_on_method("patch", 422, "Validation Error")
            .with_error_on_method("put", 422, "Validation Error")
            .with_error_on_method("delete", 403, "Forbidden")
            .build()
        )

    @staticmethod
    def paginated_list(items: List[Any] = None, total: int = 100) -> MagicMock:
        """Mock client configured for paginated list responses.

        Args:
            items: Items to return in the page
            total: Total number of items across all pages

        Returns:
            Mock client with pagination configured
        """
        return (
            MockClientBuilder()
            .with_pagination(items=items, total=total)
            .build()
        )
