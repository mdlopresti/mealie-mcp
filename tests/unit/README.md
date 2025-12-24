# Unit Tests

Unit tests for the Mealie MCP Server testing individual components in isolation.

## Overview

Unit tests focus on testing **individual functions and methods** without external dependencies:
- ✅ No real HTTP calls (httpx mocked)
- ✅ No Docker containers
- ✅ No MCP server process
- ✅ Fast execution (<1s per test)
- ✅ Isolated test environment

## Directory Structure

```
tests/unit/
├── conftest.py              # Unit test fixtures and mocks
├── test_client_unit.py      # MealieClient method tests
├── test_tools_unit.py       # MCP tool function tests
└── README.md                # This file
```

## Quick Start

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/test_client_unit.py -v

# Run tests matching pattern
pytest tests/unit/ -k "recipe" -v

# Run with coverage
pytest tests/unit/ --cov=src --cov-report=term-missing
```

## Test Fixtures

### Mock HTTP Client

```python
def test_example(mock_httpx_client, mock_mealie_client):
    """Test with mocked HTTP responses."""
    # Configure mock response
    mock_httpx_client.get.return_value.json.return_value = {"name": "Test"}
    mock_httpx_client.get.return_value.status_code = 200
    
    # Test client method
    result = mock_mealie_client.get_recipe("test-slug")
    
    # Verify
    assert result["name"] == "Test"
    mock_httpx_client.get.assert_called_once()
```

### Sample Response Data

```python
def test_with_sample_data(sample_recipe_response):
    """Test using pre-configured sample data."""
    # sample_recipe_response is a complete recipe dict
    assert sample_recipe_response["name"] == "Test Recipe"
    assert "recipeIngredient" in sample_recipe_response
```

### Pre-configured Responses

```python
def test_success(mock_successful_response):
    """Test with 200 OK response."""
    assert mock_successful_response.status_code == 200
    assert "id" in mock_successful_response.json()

def test_error(mock_error_response):
    """Test with 404 Not Found response."""
    assert mock_error_response.status_code == 404
    # Response raises HTTPStatusError on raise_for_status()
```

## Available Fixtures

### Client Fixtures
- `mock_httpx_client` - Mocked httpx.Client (no real HTTP)
- `mock_mealie_client` - MealieClient with mocked HTTP client

### Response Fixtures
- `mock_httpx_response` - Generic mock response
- `mock_successful_response` - Pre-configured 200 OK
- `mock_error_response` - Pre-configured 404 Not Found
- `mock_server_error_response` - Pre-configured 500 Server Error

### Sample Data Fixtures
- `sample_recipe_response` - Complete recipe data
- `sample_mealplan_response` - Complete meal plan data
- `sample_shopping_list_response` - Complete shopping list data

## Writing Unit Tests

### Test Pattern

```python
import pytest
from unittest.mock import Mock

@pytest.mark.unit
def test_feature_success(mock_mealie_client, mock_httpx_client):
    """Test successful feature operation."""
    # Arrange - Set up mocks
    mock_httpx_client.get.return_value.json.return_value = {"key": "value"}
    mock_httpx_client.get.return_value.status_code = 200
    mock_httpx_client.get.return_value.raise_for_status = Mock()
    
    # Act - Call the method
    result = mock_mealie_client.some_method("arg")
    
    # Assert - Verify results and calls
    assert result["key"] == "value"
    mock_httpx_client.get.assert_called_once_with("/api/endpoint")
```

### Test Error Handling

```python
@pytest.mark.unit
def test_feature_error(mock_mealie_client, mock_httpx_client):
    """Test error handling."""
    # Arrange - Configure error response
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404 Not Found",
        request=Mock(),
        response=mock_response
    )
    mock_httpx_client.get.return_value = mock_response
    
    # Act & Assert
    with pytest.raises(httpx.HTTPStatusError):
        mock_mealie_client.some_method("arg")
```

### Test Tool Functions

```python
from unittest.mock import patch

@pytest.mark.unit
def test_tool_function(sample_recipe_response):
    """Test MCP tool wrapper function."""
    # Arrange - Mock the client
    with patch('src.tools.recipes.get_client') as mock_get_client:
        mock_client = Mock()
        mock_client.get_recipe.return_value = sample_recipe_response
        mock_get_client.return_value = mock_client
        
        # Act - Call tool function
        result = recipes.get(slug="test-recipe")
        
        # Assert - Verify JSON result
        result_data = json.loads(result)
        assert result_data["name"] == "Test Recipe"
        mock_client.get_recipe.assert_called_once()
```

## Best Practices

### 1. Test Isolation
Each test should be completely independent:
```python
# Good - Uses fixtures, no shared state
def test_isolated(mock_mealie_client):
    result = mock_mealie_client.get_recipe("test")
    assert result is not None

# Bad - Shared state, tests depend on order
client = MealieClient("http://test", "token")
def test_dependent_1():
    global client
    client.create_recipe(name="Test")
```

### 2. Mock External Dependencies
Never make real HTTP calls in unit tests:
```python
# Good - HTTP client is mocked
def test_with_mock(mock_mealie_client, mock_httpx_client):
    mock_httpx_client.get.return_value.json.return_value = {"data": "value"}
    result = mock_mealie_client.get_recipe("test")

# Bad - Would make real HTTP call
def test_without_mock():
    client = MealieClient("https://real-server.com", "token")
    result = client.get_recipe("test")  # ❌ Real HTTP call!
```

### 3. Use Descriptive Test Names
```python
# Good - Clearly describes what's being tested
def test_get_recipe_returns_recipe_data_when_recipe_exists():
    ...

def test_get_recipe_raises_http_error_when_recipe_not_found():
    ...

# Bad - Vague names
def test_recipe():
    ...

def test_error():
    ...
```

### 4. Follow AAA Pattern
Arrange, Act, Assert:
```python
def test_example():
    # Arrange - Set up test data and mocks
    mock_response = {"name": "Test"}
    
    # Act - Execute the code under test
    result = function_to_test(mock_response)
    
    # Assert - Verify expected results
    assert result["name"] == "Test"
```

## Running Tests

### Run Options
```bash
# Fast - Run only unit tests
pytest tests/unit/ -v

# With markers
pytest -m unit -v

# Parallel execution (fast!)
pytest tests/unit/ -n auto

# Coverage report
pytest tests/unit/ --cov=src --cov-report=html
open htmlcov/index.html  # View coverage report

# Verbose output
pytest tests/unit/ -vv

# Stop on first failure
pytest tests/unit/ -x

# Show print statements
pytest tests/unit/ -s
```

### Performance
Unit tests are **very fast**:
- Individual test: <0.1s
- Full suite: ~2-5s
- No network, no containers, no external dependencies

## Comparison with Other Test Types

| Feature | Unit Tests | Integration Tests | E2E Tests |
|---------|-----------|------------------|-----------|
| **Speed** | ⚡ Very Fast (<1s) | 🐢 Moderate (5-10s) | 🐌 Slow (30-60s) |
| **Scope** | Single function | Multiple components | Full system |
| **Dependencies** | None (all mocked) | Some (e.g., MCP server) | All (Docker, etc.) |
| **Isolation** | ✅ Complete | ⚠️ Partial | ❌ None |
| **When to Use** | TDD, rapid feedback | API contracts | End-to-end workflows |

## When to Write Unit Tests

✅ **Write unit tests for:**
- Business logic in client methods
- Data transformation functions
- Error handling paths
- Edge cases and boundary conditions
- Tool wrapper functions

❌ **Don't write unit tests for:**
- External API behavior (use E2E tests)
- MCP protocol compliance (use E2E tests)
- Docker container setup (use E2E tests)
- End-to-end user workflows (use E2E tests)

## Examples

See example tests in:
- `test_client_unit.py` - MealieClient method tests
- `test_tools_unit.py` - MCP tool function tests

## Next Steps

After mastering unit tests:
1. **Integration Tests** (`tests/integration/`) - Test component interactions
2. **E2E Tests** (`tests/e2e/`) - Test complete workflows

## References

- pytest documentation: https://docs.pytest.org/
- unittest.mock: https://docs.python.org/3/library/unittest.mock.html
- Python mocking guide: https://realpython.com/python-mock-library/
