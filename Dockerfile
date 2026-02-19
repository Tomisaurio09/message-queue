FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install uv && uv sync --frozen

COPY src/ ./src
COPY alembic/ ./alembic

EXPOSE 8000

