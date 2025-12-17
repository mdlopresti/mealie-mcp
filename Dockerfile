# Mealie MCP Server
# FastMCP-based Model Context Protocol server for Mealie integration

FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# MCP servers communicate via stdin/stdout, no port needed
# Environment variables MEALIE_URL and MEALIE_API_TOKEN must be provided at runtime

ENTRYPOINT ["python", "-m", "src.server"]
