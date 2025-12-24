"""
Tests for Meal Plan MCP Resources.

Tests for mealplans://current, mealplans://today, and mealplans://{date} resource providers.
"""

import pytest
import respx
from httpx import Response
from datetime import date, timedelta
from tests.mcp.helpers import validate_resource_uri


class TestMealPlanResourceRegistration:
    """Test that meal plan resources are properly registered."""

    @pytest.mark.asyncio
    async def test_mealplans_current_resource_registered(self, mcp_server):
        """Test that mealplans://current resource is registered."""
        resources = await mcp_server.get_resources()
        assert "mealplans://current" in resources

    @pytest.mark.asyncio
    async def test_mealplans_today_resource_registered(self, mcp_server):
        """Test that mealplans://today resource is registered."""
        resources = await mcp_server.get_resources()
        assert "mealplans://today" in resources

    @pytest.mark.asyncio
    async def test_mealplans_date_resource_registered(self, mcp_server):
        """Test that mealplans://{date} templated resource is registered."""
        templates = await mcp_server.get_resource_templates()
        assert "mealplans://{date}" in templates

    @pytest.mark.asyncio
    async def test_mealplans_current_uri_format(self):
        """Test that mealplans://current URI follows MCP format."""
        assert validate_resource_uri("mealplans://current")

    @pytest.mark.asyncio
    async def test_mealplans_today_uri_format(self):
        """Test that mealplans://today URI follows MCP format."""
        assert validate_resource_uri("mealplans://today")

    @pytest.mark.asyncio
    async def test_mealplans_date_uri_format(self):
        """Test that mealplans://{date} URI follows MCP format."""
        assert validate_resource_uri("mealplans://2025-12-25")

    @pytest.mark.asyncio
    async def test_mealplans_current_has_description(self, mcp_server):
        """Test that mealplans://current has a description."""
        resources = await mcp_server.get_resources()
        resource = resources["mealplans://current"]
        assert resource.description is not None
        assert len(resource.description) > 0
        assert "meal" in resource.description.lower()


class TestMealPlansCurrentResource:
    """Test mealplans://current resource provider."""

    @pytest.mark.asyncio
    async def test_read_current_mealplan_empty(self, mcp_server, mealie_env):
        """Test reading current week's meal plan with no meals."""
        with respx.mock:
            # Mock empty response
            respx.get(url__regex=r".*\/api\/households\/mealplans.*").mock(
                return_value=Response(200, json=[])
            )

            resources = await mcp_server.get_resources()
            resource = resources["mealplans://current"]
            content = await resource.read()

            assert isinstance(content, str)
            assert "# Current Week's Meal Plan" in content
            assert "Week of" in content
            # Should have all 7 days
            assert "Monday" in content or "Sunday" in content

    @pytest.mark.asyncio
    async def test_read_current_mealplan_with_meals(self, mcp_server, mealie_env):
        """Test reading current week's meal plan with meals."""
        with respx.mock:
            today = date.today()
            mock_meals = [
                {
                    "id": "meal-1",
                    "date": today.isoformat(),
                    "entryType": "dinner",
                    "recipe": {
                        "name": "Pasta Carbonara",
                        "slug": "pasta-carbonara"
                    }
                },
                {
                    "id": "meal-2",
                    "date": (today + timedelta(days=1)).isoformat(),
                    "entryType": "lunch",
                    "recipe": {
                        "name": "Caesar Salad",
                        "slug": "caesar-salad"
                    }
                }
            ]
            respx.get(url__regex=r".*\/api\/households\/mealplans.*").mock(
                return_value=Response(200, json=mock_meals)
            )

            resources = await mcp_server.get_resources()
            resource = resources["mealplans://current"]
            content = await resource.read()

            # Verify meals are present
            assert "Pasta Carbonara" in content
            assert "Caesar Salad" in content

    @pytest.mark.asyncio
    async def test_read_current_mealplan_marks_today(self, mcp_server, mealie_env):
        """Test that current meal plan marks today specially."""
        with respx.mock:
            respx.get(url__regex=r".*\/api\/households\/mealplans.*").mock(
                return_value=Response(200, json=[])
            )

            resources = await mcp_server.get_resources()
            resource = resources["mealplans://current"]
            content = await resource.read()

            # Should mark today
            assert "**(TODAY)**" in content

    @pytest.mark.asyncio
    async def test_read_current_mealplan_organized_by_type(self, mcp_server, mealie_env):
        """Test that meals are organized by type (breakfast, lunch, dinner)."""
        with respx.mock:
            today = date.today()
            mock_meals = [
                {
                    "id": "meal-1",
                    "date": today.isoformat(),
                    "entryType": "breakfast",
                    "recipe": {"name": "Pancakes", "slug": "pancakes"}
                },
                {
                    "id": "meal-2",
                    "date": today.isoformat(),
                    "entryType": "lunch",
                    "recipe": {"name": "Sandwich", "slug": "sandwich"}
                },
                {
                    "id": "meal-3",
                    "date": today.isoformat(),
                    "entryType": "dinner",
                    "recipe": {"name": "Steak", "slug": "steak"}
                }
            ]
            respx.get(url__regex=r".*\/api\/households\/mealplans.*").mock(
                return_value=Response(200, json=mock_meals)
            )

            resources = await mcp_server.get_resources()
            resource = resources["mealplans://current"]
            content = await resource.read()

            # Should have meal type headers
            assert "### Breakfast" in content
            assert "### Lunch" in content
            assert "### Dinner" in content

    @pytest.mark.asyncio
    async def test_read_current_mealplan_with_notes(self, mcp_server, mealie_env):
        """Test that meal plan notes are displayed."""
        with respx.mock:
            today = date.today()
            mock_meals = [
                {
                    "id": "meal-1",
                    "date": today.isoformat(),
                    "entryType": "dinner",
                    "recipe": {"name": "Pizza", "slug": "pizza"},
                    "text": "Get extra cheese"
                }
            ]
            respx.get(url__regex=r".*\/api\/households\/mealplans.*").mock(
                return_value=Response(200, json=mock_meals)
            )

            resources = await mcp_server.get_resources()
            resource = resources["mealplans://current"]
            content = await resource.read()

            # Should display note
            assert "Get extra cheese" in content

    @pytest.mark.asyncio
    async def test_read_current_mealplan_api_error(self, mcp_server, mealie_env):
        """Test current meal plan handles API errors."""
        with respx.mock:
            respx.get(url__regex=r".*\/api\/households\/mealplans.*").mock(
                return_value=Response(500, json={"error": "Internal server error"})
            )

            resources = await mcp_server.get_resources()
            resource = resources["mealplans://current"]
            content = await resource.read()

            # Should return error message
            assert isinstance(content, str)
            assert "error" in content.lower() or "Error" in content


class TestMealPlansTodayResource:
    """Test mealplans://today resource provider."""

    @pytest.mark.asyncio
    async def test_read_today_meals_empty(self, mcp_server, mealie_env):
        """Test reading today's meals when none planned."""
        with respx.mock:
            respx.get(url__regex=r".*\/api\/households\/mealplans\/today$").mock(
                return_value=Response(200, json=[])
            )

            resources = await mcp_server.get_resources()
            resource = resources["mealplans://today"]
            content = await resource.read()

            assert isinstance(content, str)
            assert "# Meals for" in content
            assert "No meals planned" in content

    @pytest.mark.asyncio
    async def test_read_today_meals_with_meals(self, mcp_server, mealie_env):
        """Test reading today's meals."""
        with respx.mock:
            mock_meals = [
                {
                    "id": "meal-1",
                    "date": date.today().isoformat(),
                    "entryType": "breakfast",
                    "recipe": {
                        "name": "Oatmeal",
                        "slug": "oatmeal",
                        "description": "Healthy breakfast",
                        "prepTime": "5 minutes",
                        "performTime": "10 minutes",
                        "totalTime": "15 minutes"
                    }
                },
                {
                    "id": "meal-2",
                    "date": date.today().isoformat(),
                    "entryType": "dinner",
                    "recipe": {
                        "name": "Chicken Stir Fry",
                        "slug": "chicken-stir-fry"
                    }
                }
            ]
            respx.get(url__regex=r".*\/api\/households\/mealplans\/today$").mock(
                return_value=Response(200, json=mock_meals)
            )

            resources = await mcp_server.get_resources()
            resource = resources["mealplans://today"]
            content = await resource.read()

            # Verify meals are present
            assert "## Breakfast" in content
            assert "Oatmeal" in content
            assert "## Dinner" in content
            assert "Chicken Stir Fry" in content

    @pytest.mark.asyncio
    async def test_read_today_meals_shows_timing(self, mcp_server, mealie_env):
        """Test that today's meals show prep/cook times."""
        with respx.mock:
            mock_meals = [
                {
                    "id": "meal-1",
                    "date": date.today().isoformat(),
                    "entryType": "dinner",
                    "recipe": {
                        "name": "Quick Meal",
                        "slug": "quick-meal",
                        "prepTime": "10 minutes",
                        "performTime": "20 minutes",
                        "totalTime": "30 minutes"
                    }
                }
            ]
            respx.get(url__regex=r".*\/api\/households\/mealplans\/today$").mock(
                return_value=Response(200, json=mock_meals)
            )

            resources = await mcp_server.get_resources()
            resource = resources["mealplans://today"]
            content = await resource.read()

            # Should show timing
            assert "Timing:" in content or "Prep:" in content
            assert "10 minutes" in content
            assert "20 minutes" in content

    @pytest.mark.asyncio
    async def test_read_today_meals_shows_description(self, mcp_server, mealie_env):
        """Test that today's meals show recipe descriptions."""
        with respx.mock:
            mock_meals = [
                {
                    "id": "meal-1",
                    "date": date.today().isoformat(),
                    "entryType": "lunch",
                    "recipe": {
                        "name": "Salad Bowl",
                        "slug": "salad-bowl",
                        "description": "Fresh and healthy salad"
                    }
                }
            ]
            respx.get(url__regex=r".*\/api\/households\/mealplans\/today$").mock(
                return_value=Response(200, json=mock_meals)
            )

            resources = await mcp_server.get_resources()
            resource = resources["mealplans://today"]
            content = await resource.read()

            # Should show description
            assert "Fresh and healthy salad" in content

    @pytest.mark.asyncio
    async def test_read_today_meals_with_notes(self, mcp_server, mealie_env):
        """Test that today's meals show notes."""
        with respx.mock:
            mock_meals = [
                {
                    "id": "meal-1",
                    "date": date.today().isoformat(),
                    "entryType": "dinner",
                    "recipe": {"name": "Tacos", "slug": "tacos"},
                    "text": "Make extra for leftovers"
                }
            ]
            respx.get(url__regex=r".*\/api\/households\/mealplans\/today$").mock(
                return_value=Response(200, json=mock_meals)
            )

            resources = await mcp_server.get_resources()
            resource = resources["mealplans://today"]
            content = await resource.read()

            # Should show note
            assert "Make extra for leftovers" in content

    @pytest.mark.asyncio
    async def test_read_today_meals_api_error(self, mcp_server, mealie_env):
        """Test today's meals handles API errors."""
        with respx.mock:
            respx.get(url__regex=r".*\/api\/households\/mealplans\/today$").mock(
                return_value=Response(500, json={"error": "Internal server error"})
            )

            resources = await mcp_server.get_resources()
            resource = resources["mealplans://today"]
            content = await resource.read()

            # Should return error message
            assert isinstance(content, str)
            assert "error" in content.lower() or "Error" in content


class TestMealPlansDateResource:
    """Test mealplans://{date} resource provider."""

    @pytest.mark.asyncio
    async def test_read_mealplan_by_date(self, mcp_server, mealie_env):
        """Test reading meals for a specific date."""
        with respx.mock:
            test_date = "2025-12-25"
            mock_response = [
                {
                    "id": "meal-1",
                    "date": test_date,
                    "entryType": "dinner",
                    "recipe": {
                        "name": "Christmas Dinner",
                        "slug": "christmas-dinner"
                    }
                }
            ]
            respx.get(url__regex=r".*\/api\/households\/mealplans.*").mock(
                return_value=Response(200, json=mock_response)
            )

            templates = await mcp_server.get_resource_templates()
            resource = templates["mealplans://{date}"]
            content = await resource.read({"date": test_date})

            assert isinstance(content, str)
            assert "2025-12-25" in content
            assert "Christmas Dinner" in content

    @pytest.mark.asyncio
    async def test_read_mealplan_by_date_empty(self, mcp_server, mealie_env):
        """Test reading meals for a date with no meals."""
        with respx.mock:
            test_date = "2025-01-01"
            respx.get(url__regex=r".*\/api\/households\/mealplans.*").mock(
                return_value=Response(200, json=[])
            )

            templates = await mcp_server.get_resource_templates()
            resource = templates["mealplans://{date}"]
            content = await resource.read({"date": test_date})

            assert isinstance(content, str)
            assert "No meals planned" in content or "0" in content

    @pytest.mark.asyncio
    async def test_read_mealplan_by_date_api_error(self, mcp_server, mealie_env):
        """Test date-specific meal plan handles API errors."""
        with respx.mock:
            test_date = "2025-01-01"
            respx.get(url__regex=r".*\/api\/households\/mealplans.*").mock(
                return_value=Response(500, json={"error": "Internal server error"})
            )

            templates = await mcp_server.get_resource_templates()
            resource = templates["mealplans://{date}"]
            content = await resource.read({"date": test_date})

            # Should return error message
            assert isinstance(content, str)
            assert "error" in content.lower() or "Error" in content
