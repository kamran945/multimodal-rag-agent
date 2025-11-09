# Start from a lightweight official Python image
FROM python:3.12-slim

# Copy uv binaries (a fast dependency manager like pip)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install system-level dependencies
# ffmpeg is needed by PyAV (video/audio processing)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# --- Dependency Installation Layer ---
# Copy only dependency files first (for better build caching)
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-cache

# --- Application Code Layer ---
# Copy the rest of your application code after dependencies
COPY . .

# Let Python know where to find your src package
ENV PYTHONPATH=/app/src

# Entrypoint specifies the base command (Python interpreter)
ENTRYPOINT ["/app/.venv/bin/python"]

# CMD gives default arguments for the entrypoint (the script + options)
CMD ["src/multimodal_mcp/server.py", "--port", "9090"]
