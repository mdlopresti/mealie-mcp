# E2E Test Infrastructure

This document describes the end-to-end (E2E) test infrastructure for the Mealie MCP Server.

## Overview

E2E tests validate the Mealie MCP Server against a real Mealie instance. They are **optional** and skip gracefully when environment variables are not set.

## Directory Structure

```
tests/e2e/
├── __init__.py              # Package initialization with documentation
├── conftest.py              # Pytest fixtures for E2E tests
├── helpers.py               # Utility functions (retry, unique IDs, cleanup)
└── test_example_e2e.py      # Example E2E tests demonstrating infrastructure
```

## Environment Variables

E2E tests require two environment variables:

- **MEALIE_E2E_URL**: URL of the Mealie instance (e.g., `https://recipe.vilo.network`)
- **MEALIE_E2E_TOKEN**: API token for authentication

If these are not set, all E2E tests are automatically skipped.

## Fixtures

### Core Fixtures

#### `e2e_client` (session scope)
Creates a real `MealieClient` connected to the Mealie instance specified by environment variables.

```python
@pytest.mark.e2e
def test_something(e2e_client):
    recipe = e2e_client.create_recipe(name="Test Recipe")
    assert recipe["slug"] is not None
```

#### `unique_id`
Generates a unique identifier for test resources to prevent collisions.

```python
@pytest.mark.e2e
def test_something(unique_id):
    recipe_name = f"E2E Test Recipe {unique_id}"
    # Creates name like "E2E Test Recipe e2e-test-20251223-143052-123456"
```

### Cleanup Fixtures

All cleanup fixtures automatically delete tracked resources in teardown:

- **`test_recipe_cleanup`**: Track recipe slugs for cleanup
- **`test_mealplan_cleanup`**: Track meal plan IDs for cleanup
- **`test_shopping_list_cleanup`**: Track shopping list IDs for cleanup
- **`test_tag_cleanup`**: Track tag IDs for cleanup
- **`test_category_cleanup`**: Track category IDs for cleanup
- **`test_food_cleanup`**: Track food IDs for cleanup
- **`test_unit_cleanup`**: Track unit IDs for cleanup
- **`test_cookbook_cleanup`**: Track cookbook IDs for cleanup
- **`test_tool_cleanup`**: Track tool IDs for cleanup
- **`test_cleanup_all`**: Universal cleanup for multiple resource types

#### Example: Single Resource Type
```python
@pytest.mark.e2e
def test_create_recipe(e2e_client, unique_id, test_recipe_cleanup):
    recipe = e2e_client.create_recipe(name=f"Test {unique_id}")
    test_recipe_cleanup.append(recipe["slug"])
    # Recipe automatically deleted in teardown
```

#### Example: Multiple Resource Types
```python
@pytest.mark.e2e
def test_multiple_resources(e2e_client, unique_id, test_cleanup_all):
    recipe = e2e_client.create_recipe(name=f"Test {unique_id}")
    test_cleanup_all["recipes"].append(recipe["slug"])

    tag = e2e_client.create_tag(name=f"Test Tag {unique_id}")
    test_cleanup_all["tags"].append(tag["id"])

    # All resources automatically deleted in teardown
```

## Helper Functions

### `retry_on_network_error(func, max_retries=3)`
Retries a function on network errors with exponential backoff.

```python
from tests.e2e.helpers import retry_on_network_error

def flaky_operation():
    return e2e_client.create_recipe(name="Test")

recipe = retry_on_network_error(flaky_operation, max_retries=3)
```

### `generate_unique_id(prefix="e2e-test")`
Generates unique identifiers for test resources.

```python
from tests.e2e.helpers import generate_unique_id

unique_id = generate_unique_id("my-test")
# Returns: "my-test-20251223-143052-123456"
```

### `cleanup_test_data(client, resource_ids)`
Bulk cleanup helper for test resources. Ignores 404 errors (already deleted).

```python
from tests.e2e.helpers import cleanup_test_data

cleanup_test_data(e2e_client, {
    "recipes": ["recipe-1", "recipe-2"],
    "tags": ["tag-1"],
    "categories": ["cat-1"]
})
```

## Running E2E Tests

### Setup
```bash
# Set environment variables
export MEALIE_E2E_URL="https://your-mealie-instance.com"
export MEALIE_E2E_TOKEN="your-test-api-token"
```

### Run Commands
```bash
# Run only E2E tests
pytest -m e2e

# Run all tests (unit + E2E)
pytest

# Skip E2E tests (default if env vars not set)
pytest -m "not e2e"

# Run specific E2E test file
pytest tests/e2e/test_recipes_e2e.py -v
```

### Verification
```bash
# Without env vars (should skip)
pytest tests/e2e/ -v
# Output: "2 skipped (E2E environment variables not set)"

# With env vars (should collect tests)
MEALIE_E2E_URL=test MEALIE_E2E_TOKEN=test pytest tests/e2e/ --collect-only
# Output: "2 tests collected"
```

## Implementation Details

### Pytest Marker
E2E tests are marked with `@pytest.mark.e2e` which is registered in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "e2e: End-to-end tests requiring real Mealie instance"
]
```

### Graceful Skipping
Tests skip automatically if environment variables are not set using `pytestmark` at module level:

```python
# In tests/e2e/conftest.py
pytestmark = pytest.mark.skipif(
    not MEALIE_E2E_URL or not MEALIE_E2E_TOKEN,
    reason="E2E tests require MEALIE_E2E_URL and MEALIE_E2E_TOKEN environment variables"
)
```

### Retry Logic
Network errors are handled with exponential backoff:
- Initial delay: 0.5 seconds
- Backoff factor: 2.0 (0.5s → 1.0s → 2.0s)
- Max retries: 3 (4 total attempts)

### Cleanup Robustness
Cleanup fixtures:
- Ignore 404 errors (resource already deleted)
- Log but don't fail on other errors
- Execute in teardown even if test fails

## Best Practices

1. **Use unique IDs**: Always use `unique_id` fixture to prevent test collisions
2. **Track resources**: Always append created resource IDs to cleanup fixtures
3. **Use test instance**: Never run E2E tests against production Mealie
4. **Prefix test data**: Use "e2e-test-" prefix for easy identification
5. **Independent tests**: Each test should be able to run independently
6. **Clean state**: Don't rely on data from other tests
7. **Use retry**: Wrap network calls in `retry_on_network_error` for flaky tests

## Example Test

```python
import pytest
from src.client import MealieClient

@pytest.mark.e2e
def test_recipe_workflow(
    e2e_client: MealieClient,
    unique_id: str,
    test_cleanup_all: dict[str, list[str]]
):
    """
    Test complete recipe workflow: create, update, retrieve, delete.
    """
    # Create recipe with unique name
    recipe_name = f"E2E Workflow Test {unique_id}"
    recipe = e2e_client.create_recipe(
        name=recipe_name,
        description="Testing recipe workflow"
    )
    test_cleanup_all["recipes"].append(recipe["slug"])

    # Verify creation
    assert recipe["name"] == recipe_name
    assert recipe["slug"] is not None

    # Update recipe
    updated = e2e_client.update_recipe(
        slug=recipe["slug"],
        description="Updated description"
    )
    assert updated["description"] == "Updated description"

    # Retrieve recipe
    retrieved = e2e_client.get_recipe(recipe["slug"])
    assert retrieved["name"] == recipe_name
    assert retrieved["description"] == "Updated description"

    # Cleanup happens automatically via test_cleanup_all
```

## Test Statistics

- **Total E2E tests**: 2 (example tests)
- **Helper unit tests**: 13 (test retry, unique ID, cleanup)
- **Fixtures**: 10+ cleanup fixtures
- **Coverage**: E2E infrastructure fully tested with unit tests

## CI/CD Integration

E2E tests are **not** run in CI by default. To enable:

```yaml
# .github/workflows/test.yml
- name: Run E2E Tests
  if: env.MEALIE_E2E_URL != ''
  env:
    MEALIE_E2E_URL: ${{ secrets.MEALIE_E2E_URL }}
    MEALIE_E2E_TOKEN: ${{ secrets.MEALIE_E2E_TOKEN }}
  run: pytest -m e2e
```

## Troubleshooting

### Tests skip unexpectedly
- Verify environment variables are set: `echo $MEALIE_E2E_URL`
- Export variables in current shell: `export MEALIE_E2E_URL=...`

### Cleanup fails
- Check Mealie instance is accessible
- Verify API token has delete permissions
- Review logs for specific error messages

### Network timeouts
- Increase retry timeout in helper functions
- Check Mealie instance connectivity
- Verify firewall/network settings

## Future Enhancements

Planned improvements for E2E testing:

1. **Test data builders**: Factory functions for complex test data
2. **Parallel execution**: pytest-xdist support for faster test runs
3. **Test categorization**: Smoke tests, regression tests, performance tests
4. **Docker Compose setup**: Local Mealie instance for E2E testing
5. **Report generation**: HTML reports with screenshots/logs
