# Stage 1: Build Frontend
FROM node:20-alpine as frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Setup Backend
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
# --frozen: use uv.lock
# --no-install-project: don't install the package itself yet
RUN uv sync --frozen --no-install-project

# Copy application code
COPY leetcode_tracker/ ./leetcode_tracker/
COPY alembic.ini ./
COPY alembic/ ./alembic/
COPY scripts/ ./scripts/

# Copy frontend build from Stage 1
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV MODULE_NAME="leetcode_tracker.main"

# Expose port
EXPOSE 8000

# Run application
CMD ["uv", "run", "uvicorn", "leetcode_tracker.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
