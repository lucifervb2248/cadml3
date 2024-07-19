#!/bin/bash
npm install -g vercel

# Log in to Vercel (you might need to set up authentication or use an API token)
# vercel login

# Deploy with force to bypass cache
vercel --force
# Ensure the script exits if any command fails

python3.9 manage.py collectstatic
