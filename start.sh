#!/bin/bash

# Render sets PORT automatically
PORT=${PORT:-8000}

# Run FastAPI in production mode
gunicorn main:app \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --workers 4
