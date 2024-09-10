#!/bin/bash

# Exit on error
set -e

echo "Starting build process..."

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

echo "Build process completed successfully."

