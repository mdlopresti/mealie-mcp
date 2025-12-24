"""
Pytest fixtures for Docker-based E2E tests.

Provides fixtures for spinning up containerized Mealie instances using Docker Compose.
This enables true end-to-end testing with isolated, reproducible environments.
"""

import os
import time
import logging
import subprocess
from pathlib import Path
from typing import Generator, Dict, Any
import pytest
import httpx
from src.client import MealieClient

logger = logging.getLogger(__name__)

# Path to docker-compose.test.yml
DOCKER_COMPOSE_FILE = Path(__file__).parent / "docker-compose.test.yml"

# Skip all Docker E2E tests if Docker is not available
def is_docker_available() -> bool:
    """Check if Docker is available and running."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


# Mark for Docker-based E2E tests
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(
        not is_docker_available(),
        reason="Docker E2E tests require Docker to be installed and running"
    )
]


@pytest.fixture(scope="session")
def docker_compose_file() -> Path:
    """
    Provide path to the Docker Compose file for tests.

    Returns:
        Path to docker-compose.test.yml
    """
    return DOCKER_COMPOSE_FILE


@pytest.fixture(scope="session")
def docker_compose_project_name() -> str:
    """
    Generate a unique project name for Docker Compose.

    This prevents conflicts when running tests in parallel.

    Returns:
        Unique project name like "mealie-e2e-test-12345"
    """
    import random
    return f"mealie-e2e-test-{random.randint(10000, 99999)}"


@pytest.fixture(scope="session")
def mealie_container(
    docker_compose_file: Path,
    docker_compose_project_name: str
) -> Generator[Dict[str, Any], None, None]:
    """
    Start a containerized Mealie instance for E2E testing.

    This fixture:
    1. Starts Mealie container using Docker Compose
    2. Waits for container to be healthy (healthcheck passes)
    3. Yields container info (URL, ports)
    4. Tears down container and volumes after tests

    Yields:
        Dict containing:
        - base_url: URL to access Mealie (e.g., "http://localhost:9925")
        - port: Port Mealie is exposed on (9925)
        - container_name: Docker container name
    """
    logger.info(f"Starting Mealie container with project: {docker_compose_project_name}")

    # Start container with docker compose v2
    try:
        subprocess.run(
            [
                "docker", "compose",
                "-f", str(docker_compose_file),
                "-p", docker_compose_project_name,
                "up", "-d"
            ],
            check=True,
            capture_output=True,
            timeout=120
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start Mealie container: {e.stderr.decode()}")
        raise

    # Wait for container to be healthy
    logger.info("Waiting for Mealie container to be healthy...")
    max_wait = 120  # 2 minutes
    interval = 5
    elapsed = 0

    while elapsed < max_wait:
        try:
            # Check container health status
            result = subprocess.run(
                [
                    "docker", "inspect",
                    "--format", "{{.State.Health.Status}}",
                    "mealie-test"
                ],
                capture_output=True,
                timeout=5
            )

            status = result.stdout.decode().strip()
            logger.debug(f"Container health status: {status}")

            if status == "healthy":
                logger.info("Mealie container is healthy!")
                break
        except subprocess.TimeoutExpired:
            logger.warning("Health check timeout")

        time.sleep(interval)
        elapsed += interval
    else:
        # Timeout - dump container logs for debugging
        logs_result = subprocess.run(
            ["docker", "logs", "mealie-test"],
            capture_output=True
        )
        logger.error(f"Container logs:\n{logs_result.stdout.decode()}")

        # Cleanup failed container
        subprocess.run(
            [
                "docker", "compose",
                "-f", str(docker_compose_file),
                "-p", docker_compose_project_name,
                "down", "-v"
            ],
            capture_output=True
        )

        raise RuntimeError("Mealie container failed to become healthy within 2 minutes")

    # Yield container info
    container_info = {
        "base_url": "http://localhost:9925",
        "port": 9925,
        "container_name": "mealie-test",
        "project_name": docker_compose_project_name
    }

    logger.info(f"Mealie container ready at {container_info['base_url']}")

    yield container_info

    # Teardown - stop container and remove volumes
    logger.info(f"Tearing down Mealie container: {docker_compose_project_name}")
    try:
        subprocess.run(
            [
                "docker", "compose",
                "-f", str(docker_compose_file),
                "-p", docker_compose_project_name,
                "down", "-v"  # -v removes volumes for clean slate
            ],
            check=True,
            capture_output=True,
            timeout=60
        )
        logger.info("Mealie container torn down successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to tear down container: {e.stderr.decode()}")


@pytest.fixture(scope="session")
def mealie_api_token(mealie_container: Dict[str, Any]) -> str:
    """
    Create an API token for the test Mealie instance.

    This fixture:
    1. Creates a test user via Mealie's signup endpoint
    2. Logs in to get an API token
    3. Returns the token for use in tests

    Args:
        mealie_container: Container info from mealie_container fixture

    Returns:
        API token string for authenticating with Mealie
    """
    base_url = mealie_container["base_url"]

    # Create test user
    signup_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "passwordConfirm": "testpassword123",
        "group": "Home",
        "admin": True
    }

    logger.info("Creating test user in Mealie...")

    with httpx.Client(timeout=30.0) as client:
        # Sign up
        try:
            signup_response = client.post(
                f"{base_url}/api/users/register",
                json=signup_data
            )
            signup_response.raise_for_status()
            logger.info("Test user created successfully")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                # User might already exist, try to login
                logger.info("User may already exist, attempting login...")
            else:
                raise

        # Login to get token
        login_data = {
            "username": signup_data["username"],
            "password": signup_data["password"]
        }

        login_response = client.post(
            f"{base_url}/api/auth/token",
            data=login_data
        )
        login_response.raise_for_status()

        token = login_response.json()["access_token"]
        logger.info("API token obtained successfully")

        return token


@pytest.fixture(scope="session")
def docker_mealie_client(
    mealie_container: Dict[str, Any],
    mealie_api_token: str
) -> MealieClient:
    """
    Create a MealieClient connected to the Docker test instance.

    This is the main fixture for Docker-based E2E tests. Use this
    instead of e2e_client when you want tests to run against a
    containerized Mealie instance.

    Args:
        mealie_container: Container info from mealie_container fixture
        mealie_api_token: API token from mealie_api_token fixture

    Returns:
        MealieClient instance connected to containerized Mealie
    """
    return MealieClient(
        base_url=mealie_container["base_url"],
        api_token=mealie_api_token
    )


@pytest.fixture
def docker_unique_id() -> str:
    """
    Generate a unique identifier for Docker E2E test resources.

    Returns:
        Unique string like "docker-e2e-20251223-143052-123456"
    """
    from tests.e2e.helpers import generate_unique_id
    return generate_unique_id("docker-e2e")


@pytest.fixture
def docker_test_cleanup(docker_mealie_client: MealieClient) -> Generator[dict[str, list[str]], None, None]:
    """
    Universal cleanup fixture for Docker E2E tests.

    Usage:
        def test_something(docker_mealie_client, docker_test_cleanup):
            recipe = docker_mealie_client.create_recipe(name="Test")
            docker_test_cleanup["recipes"].append(recipe["slug"])

            # All resources automatically deleted in teardown

    Yields:
        Dict mapping resource types to ID lists for cleanup
    """
    from tests.e2e.helpers import cleanup_test_data

    resources = {
        "recipes": [],
        "mealplans": [],
        "shopping_lists": [],
        "tags": [],
        "categories": [],
        "foods": [],
        "units": [],
        "cookbooks": [],
        "tools": []
    }

    yield resources

    # Cleanup all tracked resources
    total_resources = sum(len(ids) for ids in resources.values())
    if total_resources > 0:
        logger.info(f"Cleaning up {total_resources} Docker test resources")
        cleanup_test_data(docker_mealie_client, resources)
