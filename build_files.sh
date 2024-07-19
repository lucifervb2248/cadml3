#!/bin/bash

# Ensure the script exits if any command fails
set -e

# Use Python 3.9 (adjust according to the supported version on Vercel)
PYTHON_VERSION="python3.9"

# Create a virtual environment
$PYTHON_VERSION -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies from requirements.txt
pip install -r requirements.txt || { echo 'Failed to install dependencies'; exit 1; }

python3.9 manage.py collectstatic
