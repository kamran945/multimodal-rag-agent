# ----------------------------------------
# Config
# ----------------------------------------
APP_NAME = multimodal-rag-ui
DEV_TAG = $(APP_NAME)-dev
PROD_TAG = $(APP_NAME)
PORT = 3000

# Detect current directory in Windows-friendly format
ifeq ($(OS),Windows_NT)
	# PowerShell-compatible full path
	APP_DIR := $(shell powershell -NoProfile -Command "Write-Host $PWD")
else
	APP_DIR := $(shell pwd)
endif

# ----------------------------------------
# Stop containers if running
# ----------------------------------------
stop-multimodal-rag-ui:
	@echo "Stopping and removing any running containers..."
	- docker stop $(APP_NAME)-dev 
	- docker rm $(APP_NAME)-dev 
	- docker stop $(APP_NAME)
	- docker rm $(APP_NAME)
	@echo "All stopped and removed."

# ----------------------------------------
# Development mode (hot reload)
# ----------------------------------------
dev-multimodal-rag-ui: stop-multimodal-rag-ui
	@echo "Building development image..."
	docker build -t $(DEV_TAG) --target dev .
	@echo "Starting development container with hot reload..."
	docker run -it -p $(PORT):3000 -v "$(APP_DIR):/app" --name $(APP_NAME)-dev $(DEV_TAG)

# ----------------------------------------
# Production mode
# ----------------------------------------
prod-multimodal-rag-ui: stop-multimodal-rag-ui
	@echo "Building production image..."
	docker build -t $(PROD_TAG) --target runner .
	@echo "Starting production container..."
	docker run -d -p $(PORT):3000 --name $(APP_NAME) $(PROD_TAG)

# ----------------------------------------
# Clean dangling resources (images, containers)
# ----------------------------------------
clean-multimodal-rag-ui: stop-multimodal-rag-ui
	@echo "Removing dangling images..."
	- docker image prune -f
	@echo "Cleanup complete."

# ----------------------------------------
# Purge failed builds and unused resources
# ----------------------------------------
purge-multimodal-rag-ui:
	@echo "Cleaning failed builds and unused resources..."
	- docker image prune -f
	- docker builder prune -f
	- docker container prune -f
	- docker volume prune -f
	- docker network prune -f
	@echo "Safe cleanup done."

# ----------------------------------------
# Purge all (including volumes)
# ----------------------------------------
purge-all-multimodal-rag-ui:
	@echo "Cleaning all unused resources..."
	- docker system prune -f --volumes
	@echo "Safe cleanup done."
