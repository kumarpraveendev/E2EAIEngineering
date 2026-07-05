FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app


# Copy workspace root files for dependency resolution
COPY pyproject.toml uv.lock ./

# Copy package files and source
COPY apps/api ./apps/api


# Install dependencies including workspace packages
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --package api

ENV PYTHONOPTIMIZE=1


ENV PATH="/app/.venv/bin:$PATH"

ENV PYTHONPATH="/app/apps/api/src:$PYTHONPATH"

# Set PATH to use the virtual environment


# Create non-root user and set permissions
RUN addgroup --system app && \
    adduser --system --ingroup app app && \
    chown -R app:app /app 
   


# Switch to non-root user
USER app

# Expose the Streamlit port
EXPOSE 8000


# Set home directory for the user
WORKDIR /app/apps/api/src

# Command to run the application
CMD ["uvicorn","api.app:app","--host", "0.0.0.0", "--port", "8000"]