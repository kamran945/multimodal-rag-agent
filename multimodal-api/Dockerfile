# Start from a lightweight official Python image
FROM python:3.12-slim

# Copy uv binaries (a fast dependency manager like pip)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install system-level dependencies
# ffmpeg for video/audio processing, libgl1 for OpenGL support
RUN apt-get update && \
    apt-get install -y ffmpeg libgl1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# --- Dependency Installation Layer ---
# Copy only dependency files first for better build caching
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-cache

# --- Application Code Layer ---
# Copy the rest of the application code
COPY . .

# Install project (editable or normal)
RUN uv pip install -e .

# Entrypoint specifies the Python interpreter
ENTRYPOINT ["/app/.venv/bin/python"]

# CMD gives default arguments for the entrypoint (your API script + options)
CMD ["src/multimodal_api/api.py", "--port", "8080", "--host", "0.0.0.0"]
