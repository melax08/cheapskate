#!/bin/bash

sleep 10

alembic -c backend/alembic.ini upgrade head

poetry run python3 -m backend.db_init

uvicorn api:app --host 0.0.0.0 --port 8000 --workers 2
