#!/usr/bin/env python
"""
Test script to verify email configuration.
Run this from the Django project root:
    python manage.py shell < tools/test_email_config.py
"""

from django.conf import settings
from django.core.mail import send_mail
import sys

print("=" * 60)
print("EMAIL CONFIGURATION TEST")
print("=" * 60)

# Check settings
print("\n1. Current Email Settings:")
print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print(f"   CONTACT_EMAIL: {getattr(settings, 'CONTACT_EMAIL', 'NOT SET')}")
print(f"   DEBUG mode: {settings.DEBUG}")

if settings.DEBUG:
    print(f"\n   ✓ DEBUG=True → Emails will print to console")
else:
    print(f"\n2. SMTP Configuration:")
    print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    
    if not settings.EMAIL_HOST_USER:
        print("   ⚠ WARNING: EMAIL_HOST_USER is not set!")
    if not settings.EMAIL_HOST_PASSWORD:
        print("   ⚠ WARNING: EMAIL_HOST_PASSWORD is not set!")

# Test sending email
print("\n3. Attempting to send test email...")
try:
    result = send_mail(
        'Test Email from Bhrikutimandap',
        'This is a test email to verify SMTP configuration.',
        settings.DEFAULT_FROM_EMAIL,
        [settings.DEFAULT_FROM_EMAIL],
        fail_silently=False,
    )
    print(f"   ✓ Email sent successfully!")
except Exception as e:
    print(f"   ✗ Email send failed: {str(e)}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ Email configuration is working!")
print("=" * 60)
