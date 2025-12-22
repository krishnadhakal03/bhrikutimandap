#!/usr/bin/env python
"""
Passenger WSGI file for deploying Django application on Hostinger shared hosting.

This file is the entry point for the Passenger application server.
It sets up the Python environment and loads the Django application.

Usage:
1. Upload this file to your project root directory on Hostinger
2. Ensure the paths match your actual directory structure
3. Update the username in the paths below
4. Make sure your virtual environment is created at the specified path
"""

import sys
import os

# IMPORTANT: Update 'username' to your actual Hostinger username
INTERP = os.path.expanduser("~/public_html/bhrikutimandap/venv/bin/python")

# Check if we're using the virtual environment Python
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Add your project directory to the sys.path
# IMPORTANT: Update 'username' to your actual Hostinger username
sys.path.insert(0, os.path.expanduser('~/public_html/bhrikutimandap'))

# Load environment variables from .env file
from dotenv import load_dotenv
project_folder = os.path.expanduser('~/public_html/bhrikutimandap')
load_dotenv(os.path.join(project_folder, '.env'))

# Set the Django settings module
# Use production_settings for production deployment
os.environ['DJANGO_SETTINGS_MODULE'] = 'market.production_settings'

# Import and initialize the Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
