#!/bin/bash

sleep 10
alembic -c backend/alembic.ini upgrade head
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 2
