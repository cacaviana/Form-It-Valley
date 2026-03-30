#!/bin/bash
set -e

cd /home/site/wwwroot

# Install dependencies in /home/antenv (persists across deploys)
if [ ! -f "/home/antenv/bin/gunicorn" ]; then
    echo "Installing dependencies (first time)..."
    rm -rf /home/antenv
    python -m venv /home/antenv
    /home/antenv/bin/pip install --no-cache-dir -r requirements.txt
fi

source /home/antenv/bin/activate

# Start the app
gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 --timeout 120
