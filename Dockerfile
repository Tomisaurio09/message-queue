FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install uv && uv sync --frozen
ENV PATH="/app/.venv/bin:$PATH"

COPY src/ ./src
COPY alembic/ ./alembic

EXPOSE 8000

