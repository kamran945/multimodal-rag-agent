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
# Multimodal API (Docker)
# -------------------------------
# Build the Docker image
build-multimodal-api:
	docker build -t multimodal-api .

# # START THE MULTIMODAL Multimodal API
# # 1. Stops any existing container (clean state)
# # 2. Builds a new Docker image
# # 3. Runs the container with correct environment and volume mappings

# Windows Version
start-multimodal-api: stop-multimodal-api
	docker build -t multimodal-api .
	docker run -d -p 8080:8080 --name multimodal-api --env-file .env multimodal-api


# # STOP AND CLEAN SERVER
# # Stops and removes the running container if it exists,
# # then deletes local cache folders related to Pixeltable and records.

# Windows Version
stop-multimodal-api:
	-docker stop multimodal-api
	-docker rm -f multimodal-api
