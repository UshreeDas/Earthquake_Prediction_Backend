APP_NAME="earthquake_prediction_backend"
APP_MODULE="app:app"   # change "app:app" → (filename:Flask app variable)
HOST="0.0.0.0"
PORT=7000
WORKERS=4

# Activate venv if needed
# source venv/bin/activate

# Run Flask with Gunicorn
exec gunicorn $APP_MODULE \
    --workers $WORKERS \
    --bind $HOST:$PORT \
    --timeout 120 \
    --log-level info