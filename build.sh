#!/bin/bash

# Exit on error
set -e

echo "Starting build process..."

# Install dependencies


# Collect static files
python manage.py collectstatic --noinput
echo "Build process completed successfully."
python manage.py runserver



