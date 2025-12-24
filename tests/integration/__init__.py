"""
Integration tests for Mealie MCP server.

Tests in this directory validate MCP protocol interactions without hitting
real API endpoints. They use mocked MealieClient responses to test:

1. MCP tool invocation and parameter validation
2. Response schema compliance with MCP protocol
3. Error handling and edge cases
4. Integration between tools and client layer

These tests sit between unit tests (isolated functions) and end-to-end tests
(full system with real API calls).
"""
