FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ADD . /app

WORKDIR /app

RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"
