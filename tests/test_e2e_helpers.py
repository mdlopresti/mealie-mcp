"""
Unit tests for E2E helper functions.

Tests the retry logic, unique ID generation, and cleanup helpers
without requiring a real Mealie instance.
"""

import time
import pytest
from unittest.mock import Mock, MagicMock
import httpx
from tests.e2e.helpers import (
    retry_on_network_error,
    generate_unique_id,
    cleanup_test_data
)


def test_retry_on_network_error_success_first_try():
    """Test that successful function returns immediately."""
    mock_func = Mock(return_value="success")

    result = retry_on_network_error(mock_func, max_retries=3)

    assert result == "success"
    assert mock_func.call_count == 1


def test_retry_on_network_error_success_after_retries():
    """Test that function retries on network errors and eventually succeeds."""
    mock_func = Mock(side_effect=[
        httpx.NetworkError("Connection failed"),
        httpx.NetworkError("Connection failed"),
        "success"
    ])

    result = retry_on_network_error(mock_func, max_retries=3)

    assert result == "success"
    assert mock_func.call_count == 3


def test_retry_on_network_error_exhausts_retries():
    """Test that function raises exception after max retries."""
    mock_func = Mock(side_effect=httpx.NetworkError("Connection failed"))

    with pytest.raises(httpx.NetworkError, match="Connection failed"):
        retry_on_network_error(mock_func, max_retries=2)

    # Should try 3 times total (initial + 2 retries)
    assert mock_func.call_count == 3


def test_retry_on_network_error_exponential_backoff():
    """Test that retry delays use exponential backoff."""
    mock_func = Mock(side_effect=[
        httpx.TimeoutException("Timeout"),
        httpx.TimeoutException("Timeout"),
        "success"
    ])

    start_time = time.time()
    result = retry_on_network_error(
        mock_func,
        max_retries=2,
        initial_delay=0.1,
        backoff_factor=2.0
    )
    elapsed = time.time() - start_time

    assert result == "success"
    # Should wait 0.1s then 0.2s = 0.3s total (with some tolerance)
    assert elapsed >= 0.3
    assert elapsed < 0.5  # Should complete quickly


def test_retry_on_network_error_non_network_error():
    """Test that non-network errors are raised immediately."""
    mock_func = Mock(side_effect=ValueError("Not a network error"))

    with pytest.raises(ValueError, match="Not a network error"):
        retry_on_network_error(mock_func, max_retries=3)

    # Should fail immediately without retries
    assert mock_func.call_count == 1


def test_generate_unique_id_default_prefix():
    """Test unique ID generation with default prefix."""
    unique_id = generate_unique_id()

    assert unique_id.startswith("e2e-test-")
    assert len(unique_id) > 20  # Should have timestamp appended


def test_generate_unique_id_custom_prefix():
    """Test unique ID generation with custom prefix."""
    unique_id = generate_unique_id(prefix="custom-prefix")

    assert unique_id.startswith("custom-prefix-")
    assert len(unique_id) > 20


def test_generate_unique_id_uniqueness():
    """Test that generated IDs are unique."""
    id1 = generate_unique_id()
    time.sleep(0.001)  # Ensure different microsecond timestamp
    id2 = generate_unique_id()

    assert id1 != id2


def test_cleanup_test_data_recipes():
    """Test cleanup of recipe resources."""
    mock_client = MagicMock()

    cleanup_test_data(mock_client, {
        "recipes": ["recipe-1", "recipe-2"]
    })

    assert mock_client.delete_recipe.call_count == 2
    mock_client.delete_recipe.assert_any_call("recipe-1")
    mock_client.delete_recipe.assert_any_call("recipe-2")


def test_cleanup_test_data_multiple_types():
    """Test cleanup of multiple resource types."""
    mock_client = MagicMock()

    cleanup_test_data(mock_client, {
        "recipes": ["recipe-1"],
        "shopping_lists": ["list-1"],
        "mealplans": ["meal-1"],
        "tags": ["tag-1"]
    })

    mock_client.delete_recipe.assert_called_once_with("recipe-1")
    mock_client.delete_shopping_list.assert_called_once_with("list-1")
    mock_client.delete_mealplan.assert_called_once_with("meal-1")
    mock_client.delete_tag.assert_called_once_with("tag-1")


def test_cleanup_test_data_ignores_404():
    """Test that cleanup ignores 404 errors (already deleted)."""
    mock_client = MagicMock()

    # Simulate 404 error
    error_404 = httpx.HTTPStatusError(
        "Not found",
        request=Mock(),
        response=Mock(status_code=404)
    )
    mock_client.delete_recipe.side_effect = error_404

    # Should not raise exception
    cleanup_test_data(mock_client, {"recipes": ["recipe-1"]})

    mock_client.delete_recipe.assert_called_once_with("recipe-1")


def test_cleanup_test_data_logs_other_errors():
    """Test that cleanup logs non-404 HTTP errors."""
    mock_client = MagicMock()

    # Simulate 500 error
    error_500 = httpx.HTTPStatusError(
        "Server error",
        request=Mock(),
        response=Mock(status_code=500)
    )
    mock_client.delete_recipe.side_effect = error_500

    # Should not raise exception, but logs error
    cleanup_test_data(mock_client, {"recipes": ["recipe-1"]})

    mock_client.delete_recipe.assert_called_once_with("recipe-1")


def test_cleanup_test_data_unknown_resource_type():
    """Test that cleanup warns about unknown resource types."""
    mock_client = MagicMock()

    # Should not raise exception
    cleanup_test_data(mock_client, {"unknown_type": ["id-1"]})

    # No delete methods should be called
    assert not any([
        mock_client.delete_recipe.called,
        mock_client.delete_shopping_list.called,
        mock_client.delete_mealplan.called
    ])
