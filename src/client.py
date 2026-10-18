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


def normalize_aliases(aliases: Optional[list]) -> list[Dict[str, str]]:
    """Normalize an alias list into Mealie's ``[{"name": ...}]`` payload shape.

    Mealie stores aliases on the food/unit object itself as a list of objects
    with a single ``name`` field. Accepting bare strings keeps the tool layer
    ergonomic while still producing a valid payload.

    Args:
        aliases: List of alias names (strings) and/or ``{"name": ...}`` dicts

    Returns:
        List of alias dicts, whitespace-trimmed and de-duplicated
        case-insensitively while preserving the original order and casing

    Raises:
        ValueError: If an entry is neither a string nor a dict with a name
    """
    if not aliases:
        return []

    normalized: list[Dict[str, str]] = []
    seen: set[str] = set()

    for alias in aliases:
        if isinstance(alias, str):
            name = alias.strip()
        elif isinstance(alias, dict):
            name = str(alias.get("name", "")).strip()
        else:
            raise ValueError(
                f"Alias must be a string or a dict with a 'name' key, got {type(alias).__name__}"
            )

        if not name:
            raise ValueError("Alias names cannot be empty")

        key = name.casefold()
        if key in seen:
            continue
        seen.add(key)
        normalized.append({"name": name})

    return normalized


def alias_names(item: Dict[str, Any]) -> list[str]:
    """Extract plain alias names from a food or unit object."""
    return [
        alias["name"]
        for alias in (item.get("aliases") or [])
        if isinstance(alias, dict) and alias.get("name")
    ]


def _merge_aliases(existing: list[str], to_add: list[Dict[str, str]]) -> list[Dict[str, str]]:
    """Append normalized aliases to ``existing`` names, skipping case-insensitive duplicates."""
    seen = {name.casefold() for name in existing}
    merged = [{"name": name} for name in existing]
    for alias in to_add:
        if alias["name"].casefold() not in seen:
            seen.add(alias["name"].casefold())
            merged.append(alias)
    return merged


def _drop_aliases(existing: list[str], to_remove: list[Dict[str, str]]) -> list[Dict[str, str]]:
    """Drop normalized aliases from ``existing`` names, matching case-insensitively."""
    drop = {alias["name"].casefold() for alias in to_remove}
    return [{"name": name} for name in existing if name.casefold() not in drop]


SUBSTITUTIONS_NOT_SAVED_WARNING = (
    "Substitutions were sent but Mealie returned none. The server may be running a "
    "Mealie version without ingredient substitution support."
)


# Keys a substitution entry may use. ``food`` mirrors the key an ingredient
# line uses for its own food; the camelCase ones are what Mealie returns.
SUBSTITUTION_FOOD_ID_KEYS = ("substitute_food_id", "substituteFoodId")
SUBSTITUTION_FOOD_KEYS = ("substitute_food", "substituteFood", "food")
SUBSTITUTION_KEYS = frozenset(SUBSTITUTION_FOOD_ID_KEYS + SUBSTITUTION_FOOD_KEYS + ("note",))


def _substitute_food_ref(key: str, value: Any) -> tuple[Optional[str], Optional[str]]:
    """Read ``(id, name)`` from a ``substitute_food``-style value.

    ``None`` and ``""`` mean "not given". A dict must carry an ``id`` or a
    ``name``; other keys on it (such as a full food object) are ignored.
    """
    if value is None:
        return None, None
    if isinstance(value, str):
        return None, value.strip() or None
    if isinstance(value, dict):
        food_id = value.get("id") or None
        name = str(value.get("name") or "").strip() or None
        if not food_id and not name:
            raise ValueError(f"Substitution '{key}' must include an 'id' or a 'name'")
        return (str(food_id) if food_id else None), name
    raise ValueError(
        f"Substitution '{key}' must be a food name or a dict with an 'id' or 'name', "
        f"got {type(value).__name__}"
    )


def normalize_substitutions(substitutions: Optional[list]) -> list[Dict[str, Optional[str]]]:
    """Validate substitution entries and reduce them to ``{food_id, food_name, note}``.

    Mealie stores a substitution as a substitute food ID, a free-text note, or
    both. Each entry here may be:

    - a plain string, taken as the substitute food's name
    - a dict using only these keys:
        - ``substitute_food`` (or ``food``, or Mealie's ``substituteFood``): a
          food name, or a ``{"id": ..., "name": ...}`` dict
        - ``substitute_food_id`` (or Mealie's ``substituteFoodId``)
        - ``note``

    Any other key is an error rather than being ignored, so a misspelt key
    can never turn a food substitution into a note-only one. Keys that point
    at different foods are an error too.

    Names still need resolving to IDs (see ``resolve_substitutions``); this
    function only validates, so it can run before any request is made.

    Raises:
        ValueError: If an entry is malformed or has neither a food nor a note
    """
    if not substitutions:
        return []

    normalized: list[Dict[str, Optional[str]]] = []
    for sub in substitutions:
        food_id: Optional[str] = None
        food_name: Optional[str] = None
        note: Optional[str] = None

        if isinstance(sub, str):
            food_name = sub.strip() or None
        elif isinstance(sub, dict):
            unknown = sorted(str(key) for key in set(sub) - SUBSTITUTION_KEYS)
            if unknown:
                raise ValueError(
                    f"Unknown substitution key(s): {', '.join(unknown)}. Use "
                    "substitute_food (a name or {\"id\", \"name\"}; 'food' also works), "
                    "substitute_food_id and/or note."
                )

            ids: list[tuple[str, str]] = []
            names: list[tuple[str, str]] = []
            for key in SUBSTITUTION_FOOD_ID_KEYS:
                value = sub.get(key)
                if value is None or value == "":
                    continue
                if not isinstance(value, str):
                    raise ValueError(f"Substitution '{key}' must be a string ID")
                ids.append((key, value.strip()))
            for key in SUBSTITUTION_FOOD_KEYS:
                ref_id, ref_name = _substitute_food_ref(key, sub.get(key))
                if ref_id:
                    ids.append((key, ref_id))
                if ref_name:
                    names.append((key, ref_name))

            if len({value for _, value in ids}) > 1:
                raise ValueError(
                    "Substitution keys point at different foods: "
                    + ", ".join(f"{key}={value}" for key, value in ids)
                )
            if not ids and len({value.casefold() for _, value in names}) > 1:
                raise ValueError(
                    "Substitution keys name different foods: "
                    + ", ".join(f"{key}={value!r}" for key, value in names)
                )
            food_id = ids[0][1] if ids else None
            food_name = names[0][1] if names else None

            raw_note = sub.get("note")
            if raw_note is not None and not isinstance(raw_note, str):
                raise ValueError("Substitution note must be a string")
            note = (raw_note or "").strip() or None
        else:
            raise ValueError(
                f"Substitution must be a food name or a dict, got {type(sub).__name__}"
            )

        if not food_id and not food_name and not note:
            raise ValueError("A substitution needs a substitute food, a note, or both")

        normalized.append({
            "food_id": food_id,
            "food_name": food_name,
            "note": note,
        })

    return normalized


def food_name_index(foods: list[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Map case-folded food names, plural names and aliases to ``{id, name}``.

    Names win over plural names, which win over aliases, so an alias on one
    food never shadows another food's real name.
    """
    index: Dict[str, Dict[str, Any]] = {}
    for keys in (
        lambda f: [f.get("name")],
        lambda f: [f.get("pluralName")],
        alias_names,
    ):
        for food in foods:
            if not food.get("id"):
                continue
            for key in keys(food):
                if key and key.strip().casefold() not in index:
                    index[key.strip().casefold()] = {"id": food["id"], "name": food.get("name")}
    return index


def resolve_substitutions(
    substitutions: list[Dict[str, Optional[str]]],
    index: Dict[str, Dict[str, Any]]
) -> tuple[list[Dict[str, Optional[str]]], list[str]]:
    """Turn normalized substitutions into Mealie payload entries.

    Args:
        substitutions: Output of ``normalize_substitutions``
        index: Output of ``food_name_index``, used for entries given by name

    Returns:
        ``(payload, unmatched)``: the ``{"substituteFoodId", "note"}`` entries
        Mealie accepts, and the food names that matched no existing food
        (those entries are left out of the payload). A substitute food that
        appears twice keeps its first entry, as Mealie itself would.
    """
    payload: list[Dict[str, Optional[str]]] = []
    unmatched: list[str] = []
    seen: set[str] = set()
    for sub in substitutions:
        food_id = sub["food_id"]
        if not food_id and sub["food_name"]:
            match = index.get(sub["food_name"].casefold())
            if not match or not match.get("id"):
                if sub["food_name"] not in unmatched:
                    unmatched.append(sub["food_name"])
                continue
            food_id = match["id"]
        if food_id:
            if food_id in seen:
                continue
            seen.add(food_id)
        payload.append({"substituteFoodId": food_id, "note": sub["note"]})
    return payload, unmatched


def substitutions_need_lookup(substitutions: list[Dict[str, Optional[str]]]) -> bool:
    """Whether any normalized substitution names a food without giving its ID."""
    return any(sub["food_name"] and not sub["food_id"] for sub in substitutions)


def substitution_summary(item: Dict[str, Any]) -> list[Dict[str, Any]]:
    """Flatten a food's or ingredient line's substitutions for display.

    Returns ``[{"substitute_food_id", "substitute_food", "note"}]``, where
    ``substitute_food`` is the resolved food name Mealie returned, if any.
    """
    summary = []
    for sub in item.get("substitutions") or []:
        if not isinstance(sub, dict):
            continue
        food = sub.get("substituteFood") or {}
        summary.append({
            "substitute_food_id": sub.get("substituteFoodId") or food.get("id"),
            "substitute_food": food.get("name"),
            "note": sub.get("note"),
        })
    return summary


def _existing_substitutions(food: Dict[str, Any]) -> list[Dict[str, Optional[str]]]:
    """A food's current substitutions as payload entries."""
    return [
        {"substituteFoodId": sub["substitute_food_id"], "note": sub["note"]}
        for sub in substitution_summary(food)
    ]


def _merge_substitutions(
    existing: list[Dict[str, Optional[str]]],
    to_add: list[Dict[str, Optional[str]]]
) -> list[Dict[str, Optional[str]]]:
    """Add substitutions to ``existing``.

    A substitute food that is already present has its note replaced when the
    new entry carries one. A note-only entry is skipped if the same note
    (case-insensitively) is already there.
    """
    merged = [dict(sub) for sub in existing]
    for sub in to_add:
        if sub["substituteFoodId"]:
            current = next(
                (m for m in merged if m["substituteFoodId"] == sub["substituteFoodId"]), None
            )
            if current is None:
                merged.append(dict(sub))
            elif sub["note"]:
                current["note"] = sub["note"]
        else:
            note = (sub["note"] or "").casefold()
            if not any(
                not m["substituteFoodId"] and (m["note"] or "").casefold() == note for m in merged
            ):
                merged.append(dict(sub))
    return merged


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
        label_id: Optional[str] = None,
        aliases: Optional[list] = None,
        substitutions: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Create a new food item.

        Args:
            name: The food name
            description: Optional description
            label_id: Optional label ID (UUID) to assign
            aliases: Optional alternate names the ingredient parser should
                recognize for this food (e.g. ["scallions"] for "green onion")
            substitutions: Optional standing substitutions for this food; see
                ``normalize_substitutions`` for the accepted entry shapes.
                Substitute foods given by name must already exist.

        Returns:
            Created food data with id

        Raises:
            ValueError: If a substitution is malformed or names an unknown food
            MealieAPIError: If creation fails
        """
        payload: Dict[str, Any] = {"name": name}
        if description is not None:
            payload["description"] = description
        if label_id is not None:
            payload["labelId"] = label_id
        if aliases is not None:
            payload["aliases"] = normalize_aliases(aliases)
        if substitutions is not None:
            payload["substitutions"] = self.substitution_payload(substitutions)
        return self.post("/api/foods", json=payload)

    def create_unit(
        self,
        name: str,
        description: Optional[str] = None,
        abbreviation: Optional[str] = None,
        aliases: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Create a new measurement unit.

        Args:
            name: The unit name
            description: Optional description
            abbreviation: Optional abbreviation (e.g., "tsp", "oz")
            aliases: Optional alternate names the ingredient parser should
                recognize for this unit (e.g. ["tblsp"] for "tablespoon")

        Returns:
            Created unit data with id

        Raises:
            MealieAPIError: If creation fails
        """
        payload = {"name": name}
        if description is not None:
            payload["description"] = description
        if abbreviation is not None:
            payload["abbreviation"] = abbreviation
        if aliases is not None:
            payload["aliases"] = normalize_aliases(aliases)
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
                - substitutions: list of {"substituteFoodId", "note"} (optional)

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

    def list_foods(
        self,
        page: int = 1,
        per_page: int = 50,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """List foods with pagination and an optional name search.

        Args:
            page: Page number (1-indexed)
            per_page: Number of foods per page
            search: Optional search string; Mealie matches it against the
                name (case-insensitive substring), which makes it the quickest
                way to find an existing food before adding an alias to it
        """
        params: Dict[str, Any] = {"page": page, "perPage": per_page}
        if search:
            params["search"] = search
        return self.get("/api/foods", params=params)

    def get_food(self, food_id: str) -> Dict[str, Any]:
        """Get a specific food by ID."""
        return self.get(f"/api/foods/{food_id}")

    def update_food(
        self,
        food_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        label_id: Optional[str] = None,
        aliases: Optional[list] = None,
        substitutions: Optional[list] = None
    ) -> Dict[str, Any]:
        """Update an existing food.

        Args:
            food_id: The food's ID
            name: New name for the food
            description: New description
            label_id: New label ID (UUID) to assign to the food
            aliases: Replacement alias list. Pass ``[]`` to clear all aliases,
                or omit to leave the existing aliases untouched.
            substitutions: Replacement substitution list. Pass ``[]`` to clear
                them, or omit to leave them untouched. Substitute foods given
                by name must already exist.

        Returns:
            Updated food object

        Raises:
            ValueError: If a substitution is malformed or names an unknown food

        Note:
            The Mealie API requires PUT with the full food object.
            This method fetches the current food first, then updates it.
        """
        # Validate input before making any request
        new_aliases = normalize_aliases(aliases) if aliases is not None else None
        new_substitutions = (
            self.substitution_payload(substitutions, food_id=food_id)
            if substitutions is not None else None
        )

        # GET current food to preserve all fields
        current_food = self.get(f"/api/foods/{food_id}")

        # Update only the provided fields
        if name is not None:
            current_food["name"] = name
        if description is not None:
            current_food["description"] = description
        if label_id is not None:
            current_food["labelId"] = label_id
        if new_aliases is not None:
            current_food["aliases"] = new_aliases
        if new_substitutions is not None:
            current_food["substitutions"] = new_substitutions

        # PUT the complete updated object
        return self.put(f"/api/foods/{food_id}", json=current_food)

    def get_food_aliases(self, food_id: str) -> list[str]:
        """List the alias names currently registered for a food."""
        return alias_names(self.get(f"/api/foods/{food_id}"))

    def add_food_aliases(self, food_id: str, aliases: list) -> Dict[str, Any]:
        """Add aliases to a food, preserving any that already exist.

        Aliases already present (compared case-insensitively) are skipped, so
        this is safe to call repeatedly.

        Args:
            food_id: The food's ID
            aliases: Alias names to add

        Returns:
            Updated food object
        """
        to_add = normalize_aliases(aliases)  # validate before any request
        current_food = self.get(f"/api/foods/{food_id}")
        current_food["aliases"] = _merge_aliases(alias_names(current_food), to_add)
        return self.put(f"/api/foods/{food_id}", json=current_food)

    def remove_food_aliases(self, food_id: str, aliases: list) -> Dict[str, Any]:
        """Remove aliases from a food, matching names case-insensitively.

        Args:
            food_id: The food's ID
            aliases: Alias names to remove

        Returns:
            Updated food object
        """
        to_remove = normalize_aliases(aliases)  # validate before any request
        current_food = self.get(f"/api/foods/{food_id}")
        current_food["aliases"] = _drop_aliases(alias_names(current_food), to_remove)
        return self.put(f"/api/foods/{food_id}", json=current_food)

    def list_all_foods(self) -> list[Dict[str, Any]]:
        """Fetch every food in one request (``perPage=-1``)."""
        result = self.get("/api/foods", params={"page": 1, "perPage": -1})
        return result.get("items", []) if isinstance(result, dict) else result

    def get_food_name_index(self) -> Dict[str, Dict[str, Any]]:
        """Map every food's name, plural name and aliases to its ``{id, name}``."""
        return food_name_index(self.list_all_foods())

    def substitution_payload(
        self,
        substitutions: list,
        food_id: Optional[str] = None
    ) -> list[Dict[str, Optional[str]]]:
        """Validate substitutions and resolve food names, for a food payload.

        Entries are validated before any request is made, and the food list is
        only fetched when an entry names a food without its ID.

        Args:
            substitutions: Substitution entries (see ``normalize_substitutions``)
            food_id: The food being updated, if any, to reject it as its own
                substitute before Mealie does

        Raises:
            ValueError: If an entry is malformed, names a food that does not
                exist (substitutes are never created implicitly here), or
                makes the food a substitute for itself
        """
        normalized = normalize_substitutions(substitutions)
        if food_id and any(sub["food_id"] == food_id for sub in normalized):
            raise ValueError("A food cannot be substituted with itself")
        index = self.get_food_name_index() if substitutions_need_lookup(normalized) else {}
        payload, unmatched = resolve_substitutions(normalized, index)
        if unmatched:
            raise ValueError(
                "No existing food matches substitute food name(s): "
                + ", ".join(unmatched)
                + ". Create the food first, alias the name onto an existing food, "
                "or pass substitute_food_id."
            )
        if food_id and any(sub["substituteFoodId"] == food_id for sub in payload):
            raise ValueError("A food cannot be substituted with itself")
        return payload

    def add_food_substitutions(self, food_id: str, substitutions: list) -> Dict[str, Any]:
        """Add substitutions to a food, preserving the existing ones.

        A substitute food the food already has keeps its place; its note is
        replaced only when the new entry has one. Repeated note-only entries
        are skipped, so this is safe to call repeatedly.

        Args:
            food_id: The food's ID
            substitutions: Substitutions to add

        Returns:
            Updated food object
        """
        to_add = self.substitution_payload(substitutions, food_id=food_id)
        current_food = self.get(f"/api/foods/{food_id}")
        current_food["substitutions"] = _merge_substitutions(
            _existing_substitutions(current_food), to_add
        )
        return self.put(f"/api/foods/{food_id}", json=current_food)

    def remove_food_substitutions(self, food_id: str, substitutions: list) -> Dict[str, Any]:
        """Remove substitutions from a food.

        An entry with a substitute food (by ID, or by name, plural name or
        alias, case-insensitively) removes that food's substitution whatever
        its note. A note-only entry removes note-only substitutions with the
        same note. Entries that match nothing are ignored.

        Args:
            food_id: The food's ID
            substitutions: Substitutions to remove

        Returns:
            Updated food object
        """
        to_remove = normalize_substitutions(substitutions)  # validate before any request
        current_food = self.get(f"/api/foods/{food_id}")
        index = self.get_food_name_index() if substitutions_need_lookup(to_remove) else {}

        def matches(sub: Dict[str, Any], target: Dict[str, Optional[str]]) -> bool:
            if target["food_id"]:
                return sub["substitute_food_id"] == target["food_id"]
            if target["food_name"]:
                name = target["food_name"].casefold()
                resolved = index.get(name, {}).get("id")
                return bool(resolved and sub["substitute_food_id"] == resolved) or (
                    (sub["substitute_food"] or "").casefold() == name
                )
            return not sub["substitute_food_id"] and (
                (sub["note"] or "").casefold() == (target["note"] or "").casefold()
            )

        current_food["substitutions"] = [
            {"substituteFoodId": sub["substitute_food_id"], "note": sub["note"]}
            for sub in substitution_summary(current_food)
            if not any(matches(sub, target) for target in to_remove)
        ]
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

    def list_units(
        self,
        page: int = 1,
        per_page: int = 50,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """List units with pagination and an optional name search.

        Args:
            page: Page number (1-indexed)
            per_page: Number of units per page
            search: Optional search string; Mealie matches it against the
                name (case-insensitive substring), which makes it the quickest
                way to find an existing unit before adding an alias to it
        """
        params: Dict[str, Any] = {"page": page, "perPage": per_page}
        if search:
            params["search"] = search
        return self.get("/api/units", params=params)

    def get_unit(self, unit_id: str) -> Dict[str, Any]:
        """Get a specific unit by ID."""
        return self.get(f"/api/units/{unit_id}")

    def update_unit(
        self,
        unit_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        abbreviation: Optional[str] = None,
        aliases: Optional[list] = None
    ) -> Dict[str, Any]:
        """Update an existing unit.

        Args:
            unit_id: The unit's ID
            name: New name for the unit
            description: New description
            abbreviation: New abbreviation (e.g., "tsp", "oz")
            aliases: Replacement alias list. Pass ``[]`` to clear all aliases,
                or omit to leave the existing aliases untouched.

        Returns:
            Updated unit object

        Note:
            ``/api/units/{id}`` only supports PUT with the full unit object, so
            this method fetches the current unit first and merges into it. A
            partial PATCH drops every field that is not sent.
        """
        # Validate input before making any request
        new_aliases = normalize_aliases(aliases) if aliases is not None else None

        current_unit = self.get(f"/api/units/{unit_id}")

        if name is not None:
            current_unit["name"] = name
        if description is not None:
            current_unit["description"] = description
        if abbreviation is not None:
            current_unit["abbreviation"] = abbreviation
        if new_aliases is not None:
            current_unit["aliases"] = new_aliases

        return self.put(f"/api/units/{unit_id}", json=current_unit)

    def get_unit_aliases(self, unit_id: str) -> list[str]:
        """List the alias names currently registered for a unit."""
        return alias_names(self.get(f"/api/units/{unit_id}"))

    def add_unit_aliases(self, unit_id: str, aliases: list) -> Dict[str, Any]:
        """Add aliases to a unit, preserving any that already exist.

        Aliases already present (compared case-insensitively) are skipped, so
        this is safe to call repeatedly.

        Args:
            unit_id: The unit's ID
            aliases: Alias names to add

        Returns:
            Updated unit object
        """
        to_add = normalize_aliases(aliases)  # validate before any request
        current_unit = self.get(f"/api/units/{unit_id}")
        current_unit["aliases"] = _merge_aliases(alias_names(current_unit), to_add)
        return self.put(f"/api/units/{unit_id}", json=current_unit)

    def remove_unit_aliases(self, unit_id: str, aliases: list) -> Dict[str, Any]:
        """Remove aliases from a unit, matching names case-insensitively.

        Args:
            unit_id: The unit's ID
            aliases: Alias names to remove

        Returns:
            Updated unit object
        """
        to_remove = normalize_aliases(aliases)  # validate before any request
        current_unit = self.get(f"/api/units/{unit_id}")
        current_unit["aliases"] = _drop_aliases(alias_names(current_unit), to_remove)
        return self.put(f"/api/units/{unit_id}", json=current_unit)

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
    # Cookbooks Management
    # -------------------------------------------------------------------------

    def list_cookbooks(self) -> Dict[str, Any]:
        """List all cookbooks."""
        return self.get("/api/households/cookbooks")

    def create_cookbook(
        self,
        name: str,
        description: Optional[str] = None,
        slug: Optional[str] = None,
        public: bool = False
    ) -> Dict[str, Any]:
        """Create a new cookbook."""
        payload = {"name": name, "public": public}
        if description is not None:
            payload["description"] = description
        if slug is not None:
            payload["slug"] = slug
        return self.post("/api/households/cookbooks", json=payload)

    def get_cookbook(self, cookbook_id: str) -> Dict[str, Any]:
        """Get a specific cookbook by ID."""
        return self.get(f"/api/households/cookbooks/{cookbook_id}")

    def update_cookbook(
        self,
        cookbook_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        slug: Optional[str] = None,
        public: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Update a cookbook."""
        payload = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if slug is not None:
            payload["slug"] = slug
        if public is not None:
            payload["public"] = public
        return self.put(f"/api/households/cookbooks/{cookbook_id}", json=payload)

    def delete_cookbook(self, cookbook_id: str) -> None:
        """Delete a cookbook."""
        self.delete(f"/api/households/cookbooks/{cookbook_id}")

    # -------------------------------------------------------------------------
    # Recipe Comments Management
    # -------------------------------------------------------------------------

    def get_recipe_comments(self, slug: str) -> Dict[str, Any]:
        """Get all comments for a recipe."""
        return self.get(f"/api/recipes/{slug}/comments")

    def create_comment(self, recipe_id: str, text: str) -> Dict[str, Any]:
        """Create a new comment on a recipe."""
        payload = {"recipeId": recipe_id, "text": text}
        return self.post("/api/comments", json=payload)

    def get_comment(self, comment_id: str) -> Dict[str, Any]:
        """Get a specific comment by ID."""
        return self.get(f"/api/comments/{comment_id}")

    def update_comment(self, comment_id: str, text: str) -> Dict[str, Any]:
        """Update a comment."""
        payload = {"text": text}
        return self.put(f"/api/comments/{comment_id}", json=payload)

    def delete_comment(self, comment_id: str) -> None:
        """Delete a comment."""
        self.delete(f"/api/comments/{comment_id}")

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
    # Recipe Timeline Events
    # -------------------------------------------------------------------------

    def list_timeline_events(
        self,
        page: int = 1,
        per_page: int = 50,
        order_by: Optional[str] = None,
        order_direction: Optional[str] = None,
        query_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List all recipe timeline events with pagination.

        Args:
            page: Page number (1-indexed)
            per_page: Number of events per page
            order_by: Field to order by
            order_direction: "asc" or "desc"
            query_filter: Filter query string

        Returns:
            Paginated timeline events data
        """
        params = {"page": page, "perPage": per_page}
        if order_by:
            params["orderBy"] = order_by
        if order_direction:
            params["orderDirection"] = order_direction
        if query_filter:
            params["queryFilter"] = query_filter

        return self.get("/api/recipes/timeline/events", params=params)

    def get_timeline_event(self, event_id: str) -> Dict[str, Any]:
        """
        Get a specific timeline event by ID.

        Args:
            event_id: Timeline event ID (UUID)

        Returns:
            Timeline event data
        """
        return self.get(f"/api/recipes/timeline/events/{event_id}")

    def create_timeline_event(
        self,
        recipe_id: str,
        subject: str,
        event_type: str = "info",
        event_message: Optional[str] = None,
        user_id: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new timeline event for a recipe.

        Args:
            recipe_id: Recipe ID (UUID)
            subject: Event subject/title
            event_type: Event type ("system", "info", or "comment")
            event_message: Optional event message/description
            user_id: Optional user ID (UUID)
            timestamp: Optional ISO 8601 timestamp

        Returns:
            Created timeline event data
        """
        payload = {
            "recipeId": recipe_id,
            "subject": subject,
            "eventType": event_type,
        }
        if event_message is not None:
            payload["eventMessage"] = event_message
        if user_id is not None:
            payload["userId"] = user_id
        if timestamp is not None:
            payload["timestamp"] = timestamp

        return self.post("/api/recipes/timeline/events", json=payload)

    def update_timeline_event(
        self,
        event_id: str,
        subject: Optional[str] = None,
        event_type: Optional[str] = None,
        event_message: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update an existing timeline event.

        Args:
            event_id: Timeline event ID (UUID)
            subject: New subject/title
            event_type: New event type ("system", "info", or "comment")
            event_message: New event message/description
            timestamp: New ISO 8601 timestamp

        Returns:
            Updated timeline event data
        """
        payload = {}
        if subject is not None:
            payload["subject"] = subject
        if event_type is not None:
            payload["eventType"] = event_type
        if event_message is not None:
            payload["eventMessage"] = event_message
        if timestamp is not None:
            payload["timestamp"] = timestamp

        return self.put(f"/api/recipes/timeline/events/{event_id}", json=payload)

    def delete_timeline_event(self, event_id: str) -> None:
        """
        Delete a timeline event.

        Args:
            event_id: Timeline event ID (UUID)
        """
        return self.delete(f"/api/recipes/timeline/events/{event_id}")

    def update_timeline_event_image(
        self,
        event_id: str,
        image_data: bytes,
        extension: str,
    ) -> Dict[str, Any]:
        """
        Upload or update an image for a timeline event.

        Args:
            event_id: Timeline event ID (UUID)
            image_data: Raw image bytes
            extension: Image file extension (e.g., "jpg", "png")

        Returns:
            Updated timeline event data
        """
        files = {
            "image": (f"image.{extension}", image_data, f"image/{extension}")
        }
        data = {"extension": extension}

        response = self.client.put(
            self._build_url(f"/api/recipes/timeline/events/{event_id}/image"),
            files=files,
            data=data,
        )
        response.raise_for_status()
        return response.json()

    # -------------------------------------------------------------------------
    # Event Notifications Management
    # -------------------------------------------------------------------------

    def list_notifications(self) -> list[Dict[str, Any]]:
        """
        List all event notifications.

        Returns:
            List of notification configurations
        """
        return self.get("/api/households/events/notifications")

    def create_notification(
        self,
        name: str,
        apprise_url: Optional[str] = None,
        enabled: bool = True,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new event notification.

        Args:
            name: Notification name
            apprise_url: Optional Apprise notification URL
            enabled: Whether the notification is enabled (default: True)
            options: Optional notification options (event types to subscribe to)

        Returns:
            Created notification data
        """
        data: Dict[str, Any] = {"name": name, "enabled": enabled}
        if apprise_url is not None:
            data["appriseUrl"] = apprise_url
        if options is not None:
            data["options"] = options
        return self.post("/api/households/events/notifications", json=data)

    def get_notification(self, item_id: str) -> Dict[str, Any]:
        """
        Get a specific notification by ID.

        Args:
            item_id: Notification ID (UUID)

        Returns:
            Notification data
        """
        return self.get(f"/api/households/events/notifications/{item_id}")

    def update_notification(
        self,
        item_id: str,
        name: Optional[str] = None,
        apprise_url: Optional[str] = None,
        enabled: Optional[bool] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update an existing notification.

        Args:
            item_id: Notification ID (UUID)
            name: New notification name
            apprise_url: New Apprise notification URL (use None to clear)
            enabled: Whether the notification is enabled
            options: New notification options (event types to subscribe to)

        Returns:
            Updated notification data
        """
        # Get current notification to preserve required fields
        current = self.get_notification(item_id)

        data: Dict[str, Any] = {
            "id": item_id,
            "name": name if name is not None else current.get("name"),
            "groupId": current.get("groupId"),
            "householdId": current.get("householdId"),
        }

        if apprise_url is not None:
            data["appriseUrl"] = apprise_url
        if enabled is not None:
            data["enabled"] = enabled
        if options is not None:
            data["options"] = options

        return self.put(f"/api/households/events/notifications/{item_id}", json=data)

    def delete_notification(self, item_id: str) -> None:
        """
        Delete a notification.

        Args:
            item_id: Notification ID (UUID)
        """
        return self.delete(f"/api/households/events/notifications/{item_id}")

    def test_notification(self, item_id: str) -> Dict[str, Any]:
        """
        Test a notification by sending a test message.

        Args:
            item_id: Notification ID (UUID)

        Returns:
            Test result data
        """
        return self.post(f"/api/households/events/notifications/{item_id}/test", json={})

    # -------------------------------------------------------------------------
    # Webhooks Management
    # -------------------------------------------------------------------------

    def list_webhooks(self) -> Dict[str, Any]:
        """
        List all webhooks.

        Returns:
            Paginated list of webhooks
        """
        return self.get("/api/households/webhooks")

    def create_webhook(
        self,
        url: str,
        scheduled_time: str,
        enabled: bool = True,
        name: Optional[str] = None,
        webhook_type: str = "mealplan"
    ) -> Dict[str, Any]:
        """
        Create a new webhook.

        Args:
            url: Webhook URL to send notifications to
            scheduled_time: Time to trigger webhook in HH:MM:SS format
            enabled: Whether the webhook is enabled (default: True)
            name: Optional name for the webhook
            webhook_type: Type of webhook - currently only "mealplan" is supported (default: "mealplan")

        Returns:
            Created webhook data
        """
        payload = {
            "url": url,
            "scheduledTime": scheduled_time,
            "enabled": enabled,
            "webhookType": webhook_type
        }
        if name is not None:
            payload["name"] = name
        return self.post("/api/households/webhooks", json=payload)

    def get_webhook(self, item_id: str) -> Dict[str, Any]:
        """
        Get a specific webhook by ID.

        Args:
            item_id: Webhook ID (UUID)

        Returns:
            Webhook data
        """
        return self.get(f"/api/households/webhooks/{item_id}")

    def update_webhook(
        self,
        item_id: str,
        url: Optional[str] = None,
        scheduled_time: Optional[str] = None,
        enabled: Optional[bool] = None,
        name: Optional[str] = None,
        webhook_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update a webhook.

        Args:
            item_id: Webhook ID (UUID)
            url: New webhook URL
            scheduled_time: New scheduled time in HH:MM:SS format
            enabled: Whether the webhook is enabled
            name: New name for the webhook
            webhook_type: New webhook type (currently only "mealplan" is supported)

        Returns:
            Updated webhook data
        """
        payload = {}
        if url is not None:
            payload["url"] = url
        if scheduled_time is not None:
            payload["scheduledTime"] = scheduled_time
        if enabled is not None:
            payload["enabled"] = enabled
        if name is not None:
            payload["name"] = name
        if webhook_type is not None:
            payload["webhookType"] = webhook_type
        return self.put(f"/api/households/webhooks/{item_id}", json=payload)

    def delete_webhook(self, item_id: str) -> None:
        """
        Delete a webhook.

        Args:
            item_id: Webhook ID (UUID)
        """
        return self.delete(f"/api/households/webhooks/{item_id}")

    def test_webhook(self, item_id: str) -> Dict[str, Any]:
        """
        Test a webhook by sending a test notification.

        Args:
            item_id: Webhook ID (UUID)

        Returns:
            Test result data
        """
        return self.post(f"/api/households/webhooks/{item_id}/test", json={})

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

    def add_recipe_favorite(self, slug: str) -> Dict[str, Any]:
        """
        Add recipe to current user's favorites.

        Args:
            slug: Recipe slug identifier

        Returns:
            Updated user favorites data

        Raises:
            MealieAPIError: If adding favorite fails
        """
        # Get user ID first
        user = self.get("/api/users/self")
        user_id = user["id"]

        return self.post(f"/api/users/{user_id}/favorites/{slug}")

    def remove_recipe_favorite(self, slug: str) -> Dict[str, Any]:
        """
        Remove recipe from current user's favorites.

        Args:
            slug: Recipe slug identifier

        Returns:
            Updated user favorites data

        Raises:
            MealieAPIError: If removing favorite fails
        """
        # Get user ID first
        user = self.get("/api/users/self")
        user_id = user["id"]

        return self.delete(f"/api/users/{user_id}/favorites/{slug}")

    def get_user_favorites(self) -> list[Dict[str, Any]]:
        """
        Get all favorite recipes for current user.

        Returns:
            List of favorite recipe objects

        Raises:
            MealieAPIError: If fetching favorites fails
        """
        return self.get("/api/users/self/favorites")

    # -------------------------------------------------------------------------
    # Recipe Ratings Management
    # -------------------------------------------------------------------------

    def set_recipe_rating(self, slug: str, rating: float, is_favorite: Optional[bool] = None) -> Dict[str, Any]:
        """
        Set rating for a recipe (1-5 stars).

        Args:
            slug: Recipe slug identifier
            rating: Rating value (1-5 stars, or None to clear)
            is_favorite: Optional flag to mark as favorite

        Returns:
            Updated rating data

        Raises:
            MealieAPIError: If rating update fails
        """
        # Get user ID first
        user = self.get("/api/users/self")
        user_id = user["id"]

        # Build payload
        payload = {"rating": rating}
        if is_favorite is not None:
            payload["isFavorite"] = is_favorite

        return self.post(f"/api/users/{user_id}/ratings/{slug}", json=payload)

    def get_user_ratings(self) -> Dict[str, Any]:
        """
        Get all ratings for current user.

        Returns:
            User ratings data with rated recipes

        Raises:
            MealieAPIError: If fetching ratings fails
        """
        return self.get("/api/users/self/ratings")

    def get_recipe_rating(self, recipe_id: str) -> Dict[str, Any]:
        """
        Get rating for a specific recipe.

        Args:
            recipe_id: Recipe ID (UUID)

        Returns:
            Recipe rating data

        Raises:
            MealieAPIError: If fetching rating fails
        """
        return self.get(f"/api/users/self/ratings/{recipe_id}")

    # ============================================================================
    # Recipe Actions
    # ============================================================================

    def list_recipe_actions(
        self,
        page: int = 1,
        per_page: int = 50,
        order_by: Optional[str] = None,
        order_direction: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all recipe actions with pagination.

        Args:
            page: Page number (default: 1)
            per_page: Number of actions per page (default: 50)
            order_by: Field to order by
            order_direction: "asc" or "desc"

        Returns:
            Paginated action data

        Raises:
            MealieAPIError: If listing actions fails
        """
        params = {"page": page, "perPage": per_page}
        if order_by:
            params["orderBy"] = order_by
        if order_direction:
            params["orderDirection"] = order_direction

        return self.get("/api/households/recipe-actions", params=params)

    def create_recipe_action(
        self,
        action_type: str,
        title: str,
        url: str
    ) -> Dict[str, Any]:
        """
        Create a new recipe action.

        Args:
            action_type: Type of action - "link" or "post"
            title: Display title for the action
            url: URL for the action

        Returns:
            Created action data

        Raises:
            MealieAPIError: If creation fails
        """
        payload = {
            "type": action_type,
            "title": title,
            "url": url
        }
        return self.post("/api/households/recipe-actions", json=payload)

    def get_recipe_action(self, item_id: str) -> Dict[str, Any]:
        """
        Get a specific recipe action by ID.

        Args:
            item_id: Recipe action ID (UUID)

        Returns:
            Recipe action data

        Raises:
            MealieAPIError: If fetching action fails
        """
        return self.get(f"/api/households/recipe-actions/{item_id}")

    def update_recipe_action(
        self,
        item_id: str,
        action_type: Optional[str] = None,
        title: Optional[str] = None,
        url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing recipe action.

        Args:
            item_id: Recipe action ID (UUID)
            action_type: New action type
            title: New title
            url: New URL

        Returns:
            Updated action data

        Raises:
            MealieAPIError: If update fails
        """
        # Get current action to merge updates
        current = self.get_recipe_action(item_id)

        payload = {
            "id": item_id,
            "groupId": current["groupId"],
            "householdId": current["householdId"],
            "type": action_type if action_type is not None else current["type"],
            "title": title if title is not None else current["title"],
            "url": url if url is not None else current["url"]
        }

        return self.put(f"/api/households/recipe-actions/{item_id}", json=payload)

    def delete_recipe_action(self, item_id: str) -> None:
        """
        Delete a recipe action.

        Args:
            item_id: Recipe action ID (UUID)

        Raises:
            MealieAPIError: If deletion fails
        """
        self.delete(f"/api/households/recipe-actions/{item_id}")

    def trigger_recipe_action(self, item_id: str, recipe_slug: str) -> Dict[str, Any]:
        """
        Trigger a recipe action for a specific recipe.

        Args:
            item_id: Recipe action ID (UUID)
            recipe_slug: Recipe slug identifier

        Returns:
            Trigger result data

        Raises:
            MealieAPIError: If trigger fails
        """
        return self.post(f"/api/households/recipe-actions/{item_id}/trigger/{recipe_slug}")


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
