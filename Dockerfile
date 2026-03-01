FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install uv && uv sync --frozen
ENV PATH="/app/.venv/bin:$PATH"

COPY alembic.ini /app/
COPY alembic/ /app/alembic/
COPY src/ /app/src/

EXPOSE 8000

