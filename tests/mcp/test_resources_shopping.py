"""
Tests for Shopping List MCP Resources.

Tests for shopping://lists and shopping://{list_id} resource providers.
"""

import pytest
import respx
from httpx import Response
from tests.mcp.helpers import validate_resource_uri


class TestShoppingResourceRegistration:
    """Test that shopping list resources are properly registered."""

    @pytest.mark.asyncio
    async def test_shopping_lists_resource_registered(self, mcp_server):
        """Test that shopping://lists resource is registered."""
        resources = await mcp_server.get_resources()
        assert "shopping://lists" in resources

    @pytest.mark.asyncio
    async def test_shopping_list_id_resource_registered(self, mcp_server):
        """Test that shopping://{list_id} templated resource is registered."""
        templates = await mcp_server.get_resource_templates()
        assert "shopping://{list_id}" in templates

    @pytest.mark.asyncio
    async def test_shopping_lists_uri_format(self):
        """Test that shopping://lists URI follows MCP format."""
        assert validate_resource_uri("shopping://lists")

    @pytest.mark.asyncio
    async def test_shopping_list_id_uri_format(self):
        """Test that shopping://{list_id} URI follows MCP format."""
        assert validate_resource_uri("shopping://test-list-123")
        assert validate_resource_uri("shopping://abc-def-456")

    @pytest.mark.asyncio
    async def test_shopping_lists_has_description(self, mcp_server):
        """Test that shopping://lists has a description."""
        resources = await mcp_server.get_resources()
        resource = resources["shopping://lists"]
        assert resource.description is not None
        assert len(resource.description) > 0
        assert "shopping" in resource.description.lower()


class TestShoppingListsResource:
    """Test shopping://lists resource provider."""

    @pytest.mark.asyncio
    async def test_read_shopping_lists_empty(self, mcp_server, mealie_env):
        """Test reading shopping lists when none exist."""
        with respx.mock:
            # Mock empty response
            respx.get(url__regex=r".*\/api\/households\/shopping\/lists$").mock(
                return_value=Response(200, json=[])
            )

            resources = await mcp_server.get_resources()
            resource = resources["shopping://lists"]
            content = await resource.read()

            assert isinstance(content, str)
            assert "# Shopping Lists" in content
            assert "No shopping lists found" in content

    @pytest.mark.asyncio
    async def test_read_shopping_lists_with_lists(self, mcp_server, mealie_env):
        """Test reading shopping lists with data."""
        with respx.mock:
            mock_lists = [
                {
                    "id": "list-1",
                    "name": "Weekly Groceries",
                    "createdAt": "2025-12-20T10:00:00Z",
                    "updateAt": "2025-12-23T15:30:00Z",
                    "listItems": [
                        {
                            "id": "item-1",
                            "display": "2 lbs chicken",
                            "checked": False
                        },
                        {
                            "id": "item-2",
                            "display": "1 gallon milk",
                            "checked": True
                        }
                    ]
                },
                {
                    "id": "list-2",
                    "name": "Party Supplies",
                    "createdAt": "2025-12-22T12:00:00Z",
                    "listItems": []
                }
            ]
            respx.get(url__regex=r".*\/api\/households\/shopping\/lists$").mock(
                return_value=Response(200, json=mock_lists)
            )

            resources = await mcp_server.get_resources()
            resource = resources["shopping://lists"]
            content = await resource.read()

            # Verify lists are present
            assert "Total Lists**: 2" in content
            assert "Weekly Groceries" in content
            assert "Party Supplies" in content

    @pytest.mark.asyncio
    async def test_read_shopping_lists_shows_item_counts(self, mcp_server, mealie_env):
        """Test that shopping lists show item counts."""
        with respx.mock:
            mock_lists = [
                {
                    "id": "list-1",
                    "name": "Groceries",
                    "listItems": [
                        {"id": "1", "display": "Item 1", "checked": False},
                        {"id": "2", "display": "Item 2", "checked": False},
                        {"id": "3", "display": "Item 3", "checked": True}
                    ]
                }
            ]
            respx.get(url__regex=r".*\/api\/households\/shopping\/lists$").mock(
                return_value=Response(200, json=mock_lists)
            )

            resources = await mcp_server.get_resources()
            resource = resources["shopping://lists"]
            content = await resource.read()

            # Should show item counts
            assert "Total Items**: 3" in content
            assert "Completed**: 1/3" in content

    @pytest.mark.asyncio
    async def test_read_shopping_lists_shows_unchecked_items(self, mcp_server, mealie_env):
        """Test that unchecked items are shown separately."""
        with respx.mock:
            mock_lists = [
                {
                    "id": "list-1",
                    "name": "Test List",
                    "listItems": [
                        {"id": "1", "display": "Unchecked Item", "checked": False},
                        {"id": "2", "display": "Checked Item", "checked": True}
                    ]
                }
            ]
            respx.get(url__regex=r".*\/api\/households\/shopping\/lists$").mock(
                return_value=Response(200, json=mock_lists)
            )

            resources = await mcp_server.get_resources()
            resource = resources["shopping://lists"]
            content = await resource.read()

            # Should have sections for unchecked and checked
            assert "### To Buy" in content
            assert "### Already Purchased" in content
            assert "Unchecked Item" in content
            assert "Checked Item" in content

    @pytest.mark.asyncio
    async def test_read_shopping_lists_handles_paginated_response(self, mcp_server, mealie_env):
        """Test that paginated API responses are handled."""
        with respx.mock:
            # API might return items in a paginated format
            mock_response = {
                "items": [
                    {
                        "id": "list-1",
                        "name": "List 1",
                        "listItems": []
                    }
                ],
                "total": 1
            }
            respx.get(url__regex=r".*\/api\/households\/shopping\/lists$").mock(
                return_value=Response(200, json=mock_response)
            )

            resources = await mcp_server.get_resources()
            resource = resources["shopping://lists"]
            content = await resource.read()

            # Should handle both formats
            assert isinstance(content, str)
            assert "List 1" in content

    @pytest.mark.asyncio
    async def test_read_shopping_lists_shows_timestamps(self, mcp_server, mealie_env):
        """Test that shopping lists show creation/update timestamps."""
        with respx.mock:
            mock_lists = [
                {
                    "id": "list-1",
                    "name": "Timestamped List",
                    "createdAt": "2025-12-20T10:00:00Z",
                    "updateAt": "2025-12-23T15:30:00Z",
                    "listItems": []
                }
            ]
            respx.get(url__regex=r".*\/api\/households\/shopping\/lists$").mock(
                return_value=Response(200, json=mock_lists)
            )

            resources = await mcp_server.get_resources()
            resource = resources["shopping://lists"]
            content = await resource.read()

            # Should show timestamps
            assert "Created" in content or "2025-12-20" in content

    @pytest.mark.asyncio
    async def test_read_shopping_lists_api_error(self, mcp_server, mealie_env):
        """Test shopping lists handles API errors."""
        with respx.mock:
            respx.get(url__regex=r".*\/api\/households\/shopping\/lists$").mock(
                return_value=Response(500, json={"error": "Internal server error"})
            )

            resources = await mcp_server.get_resources()
            resource = resources["shopping://lists"]
            content = await resource.read()

            # Should return error message
            assert isinstance(content, str)
            assert "error" in content.lower() or "Error" in content


class TestShoppingListDetailResource:
    """Test shopping://{list_id} resource provider."""

    @pytest.mark.asyncio
    async def test_read_shopping_list_detail(self, mcp_server, mealie_env):
        """Test reading a specific shopping list."""
        with respx.mock:
            mock_list = {
                "id": "test-list-123",
                "name": "My Shopping List",
                "createdAt": "2025-12-20T10:00:00Z",
                "updateAt": "2025-12-23T15:30:00Z",
                "listItems": [
                    {
                        "id": "item-1",
                        "quantity": "2",
                        "unit": {"name": "lbs"},
                        "food": {"name": "chicken"},
                        "display": "2 lbs chicken",
                        "note": "boneless",
                        "checked": False
                    },
                    {
                        "id": "item-2",
                        "display": "1 gallon milk",
                        "checked": True
                    }
                ]
            }
            respx.get(url__regex=r".*\/api\/households\/shopping\/lists\/test-list-123$").mock(
                return_value=Response(200, json=mock_list)
            )

            templates = await mcp_server.get_resource_templates()
            resource = templates["shopping://{list_id}"]
            content = await resource.read({"list_id": "test-list-123"})

            # Verify content
            assert "# My Shopping List" in content
            assert "2 lbs chicken" in content
            assert "1 gallon milk" in content

    @pytest.mark.asyncio
    async def test_read_shopping_list_detail_shows_progress(self, mcp_server, mealie_env):
        """Test that shopping list detail shows completion progress."""
        with respx.mock:
            mock_list = {
                "id": "list-1",
                "name": "Progress List",
                "listItems": [
                    {"id": "1", "display": "Item 1", "checked": True},
                    {"id": "2", "display": "Item 2", "checked": False},
                    {"id": "3", "display": "Item 3", "checked": False}
                ]
            }
            respx.get(url__regex=r".*\/api\/households\/shopping\/lists\/list-1$").mock(
                return_value=Response(200, json=mock_list)
            )

            templates = await mcp_server.get_resource_templates()
            resource = templates["shopping://{list_id}"]
            content = await resource.read({"list_id": "list-1"})

            # Should show progress
            assert "Progress**: 1/3" in content

    @pytest.mark.asyncio
    async def test_read_shopping_list_detail_structured_items(self, mcp_server, mealie_env):
        """Test that structured shopping items are formatted correctly."""
        with respx.mock:
            mock_list = {
                "id": "list-1",
                "name": "Structured List",
                "listItems": [
                    {
                        "id": "item-1",
                        "quantity": "500",
                        "unit": {"name": "grams"},
                        "food": {"name": "flour"},
                        "note": "all-purpose",
                        "checked": False
                    }
                ]
            }
            respx.get(url__regex=r".*\/api\/households\/shopping\/lists\/list-1$").mock(
                return_value=Response(200, json=mock_list)
            )

            templates = await mcp_server.get_resource_templates()
            resource = templates["shopping://{list_id}"]
            content = await resource.read({"list_id": "list-1"})

            # Should format structured data
            assert "500 grams flour" in content or "flour" in content

    @pytest.mark.asyncio
    async def test_read_shopping_list_detail_with_notes(self, mcp_server, mealie_env):
        """Test that item notes are displayed."""
        with respx.mock:
            mock_list = {
                "id": "list-1",
                "name": "Notes List",
                "listItems": [
                    {
                        "id": "item-1",
                        "display": "Bananas",
                        "note": "Get organic if available",
                        "checked": False
                    }
                ]
            }
            respx.get(url__regex=r".*\/api\/households\/shopping\/lists\/list-1$").mock(
                return_value=Response(200, json=mock_list)
            )

            templates = await mcp_server.get_resource_templates()
            resource = templates["shopping://{list_id}"]
            content = await resource.read({"list_id": "list-1"})

            # Should show note
            assert "Get organic if available" in content

    @pytest.mark.asyncio
    async def test_read_shopping_list_detail_empty_list(self, mcp_server, mealie_env):
        """Test reading a shopping list with no items."""
        with respx.mock:
            mock_list = {
                "id": "empty-list",
                "name": "Empty List",
                "listItems": []
            }
            respx.get(url__regex=r".*\/api\/households\/shopping\/lists\/empty-list$").mock(
                return_value=Response(200, json=mock_list)
            )

            templates = await mcp_server.get_resource_templates()
            resource = templates["shopping://{list_id}"]
            content = await resource.read({"list_id": "empty-list"})

            # Should indicate no items
            assert "No items" in content

    @pytest.mark.asyncio
    async def test_read_shopping_list_detail_not_found(self, mcp_server, mealie_env):
        """Test reading a non-existent shopping list."""
        with respx.mock:
            respx.get(url__regex=r".*\/api\/households\/shopping\/lists\/nonexistent$").mock(
                return_value=Response(404, json={"error": "List not found"})
            )

            templates = await mcp_server.get_resource_templates()
            resource = templates["shopping://{list_id}"]
            content = await resource.read({"list_id": "nonexistent"})

            # Should return error message
            assert isinstance(content, str)
            assert "error" in content.lower() or "not found" in content.lower()

    @pytest.mark.asyncio
    async def test_read_shopping_list_detail_api_error(self, mcp_server, mealie_env):
        """Test shopping list detail handles API errors."""
        with respx.mock:
            respx.get(url__regex=r".*\/api\/households\/shopping\/lists\/error-list$").mock(
                return_value=Response(500, json={"error": "Internal server error"})
            )

            templates = await mcp_server.get_resource_templates()
            resource = templates["shopping://{list_id}"]
            content = await resource.read({"list_id": "error-list"})

            # Should return error message
            assert isinstance(content, str)
            assert "error" in content.lower() or "Error" in content

    @pytest.mark.asyncio
    async def test_read_shopping_list_detail_separates_checked_unchecked(self, mcp_server, mealie_env):
        """Test that checked and unchecked items are separated."""
        with respx.mock:
            mock_list = {
                "id": "list-1",
                "name": "Mixed List",
                "listItems": [
                    {"id": "1", "display": "Need to buy", "checked": False},
                    {"id": "2", "display": "Already got", "checked": True}
                ]
            }
            respx.get(url__regex=r".*\/api\/households\/shopping\/lists\/list-1$").mock(
                return_value=Response(200, json=mock_list)
            )

            templates = await mcp_server.get_resource_templates()
            resource = templates["shopping://{list_id}"]
            content = await resource.read({"list_id": "list-1"})

            # Should have separate sections
            assert "## To Buy" in content
            assert "## Already Purchased" in content
