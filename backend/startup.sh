#!/bin/bash
set -e

cd /home/site/wwwroot

# Install dependencies if gunicorn is not installed
if [ ! -f "antenv/bin/gunicorn" ]; then
    echo "Installing dependencies..."
    rm -rf antenv
    python -m venv antenv
    source antenv/bin/activate
    pip install --no-cache-dir -r requirements.txt
else
    source antenv/bin/activate
fi

# Start the app
gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 --timeout 120
