"""
End-to-end tests for Mealie MCP Server.

These tests validate against a real Mealie instance and require:
- MEALIE_E2E_URL: URL of the Mealie instance
- MEALIE_E2E_TOKEN: API token for authentication

Tests are skipped gracefully if environment variables are not set.
"""
