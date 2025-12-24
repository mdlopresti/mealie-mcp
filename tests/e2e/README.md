# E2E Test Infrastructure

This directory contains the end-to-end (E2E) test infrastructure for the Mealie MCP Server. E2E tests validate the complete integration from MCP tools down to the actual Mealie API.

## Overview

The E2E test infrastructure supports two modes:

1. **Docker-based testing** (recommended) - Tests run against containerized Mealie instances
2. **Live instance testing** - Tests run against a real Mealie server

## Docker-Based E2E Testing (Recommended)

Docker-based tests provide isolated, reproducible test environments using containerized Mealie instances.

### Prerequisites

- Docker or Podman installed and running
- Docker Compose installed
- Python development dependencies installed:
  ```bash
  pip install -r requirements-dev.txt
  ```

### Quick Start

```bash
# Run Docker E2E tests
pytest tests/e2e/test_docker_e2e.py -v

# Run with live output to see container startup
pytest tests/e2e/test_docker_e2e.py -v -s

# Run all E2E tests (Docker + Live, if configured)
pytest -m e2e
```

### How It Works

1. **Container Startup**: `mealie_container` fixture starts a fresh Mealie instance using Docker Compose
2. **Healthcheck**: Waits for container to be healthy (up to 2 minutes)
3. **User Creation**: Creates a test user and obtains an API token
4. **Client Connection**: Provides `docker_mealie_client` connected to the container
5. **Test Execution**: Tests run against the containerized instance
6. **Cleanup**: Container and volumes are destroyed after tests complete

### Docker Fixtures

#### Core Fixtures

**`mealie_container`** (session scope)
- Starts containerized Mealie instance
- Waits for health check to pass
- Returns container info (URL, port, name)
- Tears down container and volumes after session

**`mealie_api_token`** (session scope)
- Creates test user in container
- Logs in and obtains API token
- Returns token for authentication

**`docker_mealie_client`** (session scope)
- Creates MealieClient connected to container
- Uses token from `mealie_api_token`
- Main fixture for Docker E2E tests

#### Helper Fixtures

**`docker_unique_id`**
- Generates unique identifiers for test resources
- Format: `docker-e2e-YYYYMMDD-HHMMSS-NNNNNN`

**`docker_test_cleanup`**
- Universal cleanup fixture for multiple resource types
- Automatically deletes tracked resources in teardown

### Example Test

```python
import pytest
from src.client import MealieClient

@pytest.mark.e2e
def test_recipe_workflow(
    docker_mealie_client: MealieClient,
    docker_unique_id: str,
    docker_test_cleanup: dict[str, list[str]]
):
    """Test recipe creation, update, and retrieval."""

    # Create recipe
    recipe = docker_mealie_client.create_recipe(
        name=f"Test Recipe {docker_unique_id}",
        description="Docker E2E test"
    )

    # Track for cleanup
    docker_test_cleanup["recipes"].append(recipe["slug"])

    # Verify creation
    assert recipe["name"] == f"Test Recipe {docker_unique_id}"

    # Update recipe
    updated = docker_mealie_client.update_recipe(
        slug=recipe["slug"],
        description="Updated description"
    )

    # Verify update
    assert updated["description"] == "Updated description"

    # Cleanup happens automatically
```

### Configuration

The Docker Compose configuration is in `tests/e2e/docker-compose.test.yml`:

```yaml
services:
  mealie-test:
    image: ghcr.io/mealie-recipes/mealie:v1.12.0
    ports:
      - "9925:9000"
    environment:
      DB_ENGINE: sqlite
      ALLOW_SIGNUP: "true"
      BASE_URL: http://localhost:9925
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:9000/api/app/about"]
      interval: 5s
      timeout: 3s
      retries: 20
```

### Troubleshooting

**Tests skip with "Docker is not available"**
- Verify Docker is installed: `docker --version`
- Verify Docker is running: `docker info`
- For Podman: Ensure docker-compose compatibility

**Container fails to start**
- Check Docker logs: `docker logs mealie-test`
- Verify port 9925 is not in use: `lsof -i :9925`
- Check disk space for Docker volumes

**Container health check timeout**
- Container logs will be dumped automatically
- Common causes: slow system, insufficient resources
- Increase timeout in `conftest_docker.py` if needed

**Tests fail with connection errors**
- Verify container is running: `docker ps`
- Check container health: `docker inspect mealie-test`
- Test connectivity: `curl http://localhost:9925/api/app/about`

## MCP Server Lifecycle Testing

The MCP server lifecycle fixtures enable testing the complete MCP protocol integration.

### MCP Fixtures

**`mcp_server_process`** (session scope)
- Starts MCP server as subprocess
- Connects to Docker Mealie container
- Provides stdin/stdout for protocol communication
- Terminates server after session

**`mcp_client`**
- Provides interface for sending/receiving MCP messages
- Methods: `send()`, `receive()`, `call()`

**`mcp_tool_caller`**
- Simplified interface for calling MCP tools
- Example: `call_tool("mealie_recipes_get", slug="test")`

**`mcp_resource_reader`**
- Interface for reading MCP resources
- Example: `read_resource("mealie://recipes/test")`

### Example MCP Test

```python
@pytest.mark.e2e
def test_mcp_protocol(
    docker_mealie_client: MealieClient,
    mcp_tool_caller: callable,
    docker_unique_id: str,
    docker_test_cleanup: dict[str, list[str]]
):
    """Test MCP protocol integration end-to-end."""

    # Create recipe via client
    recipe = docker_mealie_client.create_recipe(
        name=f"MCP Test {docker_unique_id}"
    )
    docker_test_cleanup["recipes"].append(recipe["slug"])

    # Call MCP tool to retrieve it
    mcp_result = mcp_tool_caller(
        "mealie_recipes_get",
        slug=recipe["slug"]
    )

    # Verify MCP tool returns same data
    assert mcp_result["name"] == recipe["name"]
```

## Live Instance E2E Testing

Tests can also run against a live Mealie instance using environment variables.

### Setup

```bash
# Set environment variables
export MEALIE_E2E_URL="https://your-mealie-instance.com"
export MEALIE_E2E_TOKEN="your-test-api-token"

# Run live E2E tests
pytest tests/e2e/test_example_e2e.py -v
```

### Live Instance Fixtures

**`e2e_client`** (session scope)
- Creates MealieClient from environment variables
- Falls back to skip if variables not set

**`test_recipe_cleanup`**, **`test_mealplan_cleanup`**, etc.
- Resource-specific cleanup fixtures
- Track and delete resources after tests

**`test_cleanup_all`**
- Universal cleanup for multiple resource types

See `conftest.py` for full details on live instance fixtures.

### When to Use Live vs Docker

**Use Docker tests when:**
- ✅ You need isolated test environment
- ✅ You want reproducible test conditions
- ✅ You're testing in CI/CD
- ✅ You need a clean slate for each test run

**Use live instance tests when:**
- ✅ You're testing against a specific Mealie version
- ✅ You need to debug integration issues
- ✅ You're validating against production-like environment
- ✅ Docker is not available

## Directory Structure

```
tests/e2e/
├── README.md                    # This file
├── __init__.py                  # Package initialization
├── conftest.py                  # Live instance fixtures
├── conftest_docker.py           # Docker container fixtures
├── conftest_mcp.py              # MCP server lifecycle fixtures
├── helpers.py                   # Utility functions
├── docker-compose.test.yml      # Docker Compose configuration
├── test_docker_e2e.py           # Docker E2E tests
├── test_example_e2e.py          # Live instance E2E tests
├── test_mealplan_workflows.py  # Meal planning workflow tests
├── test_recipe_workflows.py    # Recipe workflow tests
└── test_shopping_workflows.py  # Shopping list workflow tests
```

## Test Markers

E2E tests use pytest markers for categorization:

```python
# All E2E tests
@pytest.mark.e2e

# Docker-specific tests (auto-applied by conftest_docker.py)
# Skipped if Docker not available
```

Run specific marker:
```bash
# Run all E2E tests
pytest -m e2e

# Run only Docker E2E tests
pytest tests/e2e/test_docker_e2e.py -v
```

## Best Practices

### Resource Naming
Always use unique identifiers to prevent test collisions:

```python
# Good
recipe_name = f"Test Recipe {docker_unique_id}"

# Bad - can collide with other tests
recipe_name = "Test Recipe"
```

### Cleanup
Always track created resources for cleanup:

```python
# Good
recipe = client.create_recipe(name="Test")
docker_test_cleanup["recipes"].append(recipe["slug"])

# Bad - leaves orphaned test data
recipe = client.create_recipe(name="Test")
```

### Test Isolation
Each test should be independent:

```python
# Good - creates its own data
def test_update_recipe(client, unique_id, cleanup):
    recipe = client.create_recipe(name=f"Test {unique_id}")
    cleanup["recipes"].append(recipe["slug"])
    # ... test logic ...

# Bad - depends on data from another test
def test_update_recipe(client):
    recipe = client.get_recipe("shared-test-recipe")  # ❌
```

### Error Handling
Handle expected errors gracefully:

```python
# Good - verifies error behavior
with pytest.raises(httpx.HTTPStatusError) as exc_info:
    client.get_recipe("nonexistent-recipe")
assert exc_info.value.response.status_code == 404

# Bad - lets unexpected errors fail silently
try:
    client.get_recipe("nonexistent-recipe")
except:
    pass  # ❌
```

## CI/CD Integration

Docker E2E tests can be integrated into CI/CD pipelines:

```yaml
# .github/workflows/test.yml
jobs:
  e2e-docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker
        uses: docker/setup-buildx-action@v2

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -r requirements-dev.txt

      - name: Run Docker E2E tests
        run: pytest tests/e2e/test_docker_e2e.py -v
```

## Performance Considerations

- **Container startup**: ~30-60 seconds for fresh Mealie instance
- **Test execution**: ~1-5 seconds per test
- **Container teardown**: ~5-10 seconds
- **Session scope**: Container reused across all tests in session

Optimize by:
- Using session-scoped fixtures when possible
- Running related tests together
- Parallelizing with pytest-xdist (experimental)

## Known Limitations

1. **MCP Protocol Testing**: MCP server fixtures are currently placeholders and need implementation based on FastMCP's protocol
2. **Parallel Execution**: Docker container conflicts may occur with parallel test execution
3. **Resource Cleanup**: Some resources may persist if tests crash unexpectedly
4. **Version Pinning**: Docker Compose uses Mealie v1.12.0 - update as needed

## Contributing

When adding new E2E tests:

1. Use Docker fixtures for new tests (`docker_mealie_client`)
2. Always use `docker_unique_id` for resource names
3. Track resources in `docker_test_cleanup`
4. Add docstrings explaining what the test validates
5. Follow the existing test structure and naming

## Support

For issues with E2E tests:

1. Check this README first
2. Review existing tests for examples
3. Check GitHub Issues for known problems
4. Enable verbose output: `pytest -v -s`
5. Check Docker logs: `docker logs mealie-test`

## Resources

- [Mealie API Documentation](https://nightly.mealie.io/documentation/getting-started/api/)
- [pytest-docker Documentation](https://pytest-docker.readthedocs.io/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
