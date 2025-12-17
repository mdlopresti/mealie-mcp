#!/bin/bash
# Build script for Mealie MCP Server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="mealie-mcp"
IMAGE_TAG="${1:-latest}"

echo "Building Mealie MCP Server..."
echo "Image: ${IMAGE_NAME}:${IMAGE_TAG}"

# Build the Docker image
docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" "${SCRIPT_DIR}"

echo ""
echo "Build complete!"
echo ""
echo "To run the MCP server:"
echo "  docker run -i --rm \\"
echo "    -e MEALIE_URL=https://your-mealie-instance.com \\"
echo "    -e MEALIE_API_TOKEN=your-api-token \\"
echo "    ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""
echo "To use with Claude Code, add to your MCP configuration:"
echo "  {"
echo "    \"mcpServers\": {"
echo "      \"mealie\": {"
echo "        \"command\": \"docker\","
echo "        \"args\": [\"run\", \"-i\", \"--rm\","
echo "          \"-e\", \"MEALIE_URL=https://your-mealie-instance.com\","
echo "          \"-e\", \"MEALIE_API_TOKEN=your-api-token\","
echo "          \"${IMAGE_NAME}:${IMAGE_TAG}\"]"
echo "      }"
echo "    }"
echo "  }"
