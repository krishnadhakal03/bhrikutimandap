#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
django.setup()

from store.models import SiteSettings
from django.conf import settings

# Check SiteSettings
try:
    site_settings = SiteSettings.get_instance()
    print("\n=== SiteSettings Email Configuration ===")
    print(f"Email Host: {site_settings.email_host or 'NOT SET'}")
    print(f"Email Port: {site_settings.email_port or 'NOT SET'}")
    print(f"Email Use TLS: {site_settings.email_use_tls}")
    print(f"Email Host User: {site_settings.email_host_user or 'NOT SET'}")
    print(f"Email Host Password: {'*' * len(site_settings.email_host_password) if site_settings.email_host_password else 'NOT SET'}")
    print(f"Default From Email: {site_settings.default_from_email or 'NOT SET'}")
except Exception as e:
    print(f"Error reading SiteSettings: {e}")

# Check Django settings
print("\n=== Django Settings Email Configuration ===")
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST or 'NOT SET'}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT or 'NOT SET'}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER or 'NOT SET'}")
print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
