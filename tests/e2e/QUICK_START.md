# Quick Start: Docker E2E Tests

This guide shows how to run Docker-based E2E tests in 5 minutes.

## Prerequisites

- Docker or Podman installed and running
- Python 3.12+

## Steps

### 1. Install Dependencies

```bash
# From project root
pip install -r requirements-dev.txt
```

This installs:
- pytest and pytest-cov (testing)
- pytest-docker (Docker container management)
- docker-compose (container orchestration)
- python-on-whales (modern Docker client)

### 2. Verify Docker is Running

```bash
# Check Docker is available
docker info

# Or for Podman
podman info
```

If Docker is not running, start it:
- **Linux**: `sudo systemctl start docker`
- **macOS**: Start Docker Desktop
- **Windows**: Start Docker Desktop

### 3. Run Docker E2E Tests

```bash
# Run all Docker E2E tests
pytest tests/e2e/test_docker_e2e.py -v

# Run with live output (see container startup)
pytest tests/e2e/test_docker_e2e.py -v -s

# Run specific test
pytest tests/e2e/test_docker_e2e.py::test_docker_infrastructure_recipe_workflow -v
```

### 4. Watch the Magic

The tests will:
1. ✅ Pull Mealie Docker image (if not cached)
2. ✅ Start containerized Mealie instance
3. ✅ Wait for health check (~30-60 seconds first time)
4. ✅ Create test user and get API token
5. ✅ Run tests against container
6. ✅ Clean up containers and volumes

**First run**: ~60-90 seconds (downloading images)
**Subsequent runs**: ~30-45 seconds (cached images)

## Example Output

```
$ pytest tests/e2e/test_docker_e2e.py -v

============= test session starts =============
platform linux -- Python 3.12.0
collected 5 items

tests/e2e/test_docker_e2e.py::test_docker_infrastructure_recipe_workflow PASSED [20%]
tests/e2e/test_docker_e2e.py::test_docker_infrastructure_mealplan_workflow PASSED [40%]
tests/e2e/test_docker_e2e.py::test_docker_infrastructure_shopping_list_workflow PASSED [60%]
tests/e2e/test_docker_e2e.py::test_docker_infrastructure_multiple_resources PASSED [80%]
tests/e2e/test_docker_e2e.py::test_docker_container_is_isolated PASSED [100%]

============= 5 passed in 45.23s =============
```

## Troubleshooting

### Tests Skip: "Docker is not available"

**Problem**: Docker not running or not installed

**Solution**:
```bash
# Verify Docker
docker --version
docker info

# Start Docker (Linux)
sudo systemctl start docker

# Or use Podman (with docker alias)
alias docker=podman
```

### Container Startup Timeout

**Problem**: Container fails health check within 2 minutes

**Solution**: Check Docker logs
```bash
# View container logs
docker logs mealie-test

# Common issues:
# - Insufficient disk space
# - Port 9925 already in use
# - Slow system (increase timeout in conftest_docker.py)
```

### Port Conflict

**Problem**: Port 9925 already in use

**Solution**:
```bash
# Find process using port
lsof -i :9925

# Stop conflicting service or change port in docker-compose.test.yml
```

### Permission Denied (Linux)

**Problem**: Cannot access Docker socket

**Solution**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, then test
docker ps
```

## What's Next?

- Read [README.md](README.md) for full documentation
- Look at [test_docker_e2e.py](test_docker_e2e.py) for test examples
- Create your own E2E tests following the patterns
- Check [conftest_docker.py](conftest_docker.py) for available fixtures

## Need Help?

1. Check [README.md](README.md) troubleshooting section
2. Review [test_docker_e2e.py](test_docker_e2e.py) examples
3. Enable verbose output: `pytest -v -s`
4. Check container logs: `docker logs mealie-test`
5. Open GitHub issue with logs and error details

## Tips

- **Speed up tests**: Docker caches images after first run
- **Debug tests**: Use `pytest -v -s` to see live output
- **Clean state**: Containers are destroyed after each test session
- **Parallel tests**: Not yet supported (container conflicts)
- **CI/CD**: These tests work great in GitHub Actions!
