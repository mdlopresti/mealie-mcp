# Home Assistant app image for the Mealie MCP server.
# Build context is the REPOSITORY ROOT (see .github/workflows/ha-addon.yml):
#   docker build -f mealie_mcp/Dockerfile .
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MCP_TRANSPORT=http \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8099

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY mealie_mcp/run.py ./run.py

EXPOSE 8099

LABEL io.hass.type="addon" \
      io.hass.name="Mealie MCP Server" \
      io.hass.arch="amd64|aarch64"

CMD ["python", "/app/run.py"]
