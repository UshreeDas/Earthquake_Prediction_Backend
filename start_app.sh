#!/bin/bash
APP_NAME="earthquake_prediction_backend"
APP_MODULE="main:app"
HOST="0.0.0.0"
PORT=7000
WORKERS=4

# Run FastAPI with Uvicorn
exec uvicorn $APP_MODULE \
    --host $HOST \
    --port $PORT \
    --workers $WORKERS \
    --log-level info