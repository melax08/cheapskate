#!/bin/bash

cd src
uv run alembic -c backend/alembic.ini upgrade head
uv run python3 -m backend.db_init
