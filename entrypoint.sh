#!/bin/bash

sleep 5
alembic upgrade head
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 2