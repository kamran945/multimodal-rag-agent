
# -------------------------------
# Global Settings
# -------------------------------

# CHECK_DIRS defines which directories Ruff (the linter/formatter) will scan.
# By default, "." means the current directory (the whole project).
CHECK_DIRS := .


# -------------------------------
# Ruff (Code Quality Tools)
# -------------------------------
# FORMAT + FIX IMPORTS
# Formats all code and fixes import sorting automatically.
format-fix:
	uv run ruff format $(CHECK_DIRS)
	uv run ruff check --select I --fix


# LINT + FIX
# Runs the Ruff linter and automatically fixes any fixable issues.
lint-fix:
	uv run ruff check --fix


# FORMAT CHECK ONLY
# Checks if code is properly formatted (without modifying files).
# Useful in CI pipelines or pre-commit hooks.
format-check:
	uv run ruff format --check $(CHECK_DIRS)
	uv run ruff check -e
	uv run ruff check --select I -e


# LINT CHECK ONLY
# Checks code for issues but doesn’t change anything.
lint-check:
	uv run ruff check $(CHECK_DIRS)


# -------------------------------
# MCP Server (Docker)
# -------------------------------
# Build the Docker image
build-multimodal-mcp:
	docker build -t multimodal-mcp .

# START THE MULTIMODAL MCP SERVER
# 1. Stops any existing container (clean state)
# 2. Builds a new Docker image
# 3. Runs the container with correct environment and volume mappings

# # Linux Version

# Windows Version
start-multimodal-mcp: stop-multimodal-mcp
	docker build -t multimodal-mcp .
	docker run -it -p 9090:9090 --name multimodal-mcp \
	--env-file .env \
	-v $(pwd)/notebooks/data:/app/videos \
	-v ${USERPROFILE}/.pixeltable:/root/.pixeltable \
	-v ${USERPROFILE}/.cache/huggingface:/root/.cache/huggingface \
	multimodal-mcp


# INSPECT MCP SERVER
# Installs Node.js temporarily (via nvm) and launches the
# Model Context Protocol Inspector tool for debugging MCP server.

inspect-multimodal-mcp:
	npx @modelcontextprotocol/inspector


# STOP AND CLEAN SERVER
# Stops and removes the running container if it exists,
# then deletes local cache folders related to Pixeltable and records.

# Windows Version
stop-multimodal-mcp:
	-docker stop multimodal-mcp
	-docker rm -f multimodal-mcp
	-rm -rf .pixeltable


# -------------------------------
# 4FFmpeg Utility
# -------------------------------
# FFmpeg is used for video processing. This rule re-encodes a video
# using a widely compatible format (H.264) and copies the audio track.

# FIX VIDEO ENCODING
# Usage: make fix-video input=old.mov output=new.mp4
fix-video:
	ffmpeg -i $(input) -c:v libx264 -c:a copy $(output)
