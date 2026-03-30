#!/bin/bash
set -e

# Install dependencies if venv doesn't exist
if [ ! -d "/home/site/wwwroot/antenv" ]; then
    echo "Creating virtual environment and installing dependencies..."
    cd /home/site/wwwroot
    python -m venv antenv
    source antenv/bin/activate
    pip install -r requirements.txt
else
    source /home/site/wwwroot/antenv/bin/activate
fi

# Start the app
cd /home/site/wwwroot
gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 --timeout 120
