FROM ghcr.io/astral-sh/uv:python3.14-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ADD . /app

WORKDIR /app

RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"
