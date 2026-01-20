#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
django.setup()

from django.conf import settings
from django.core import mail

print(f"Test mode: {'test' in sys.argv}")
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")

# Try sending directly
print("\n=== Testing Direct Email Send ===")

try:
    from store.views import _send_email
    
    result = _send_email(
        'Test Email',
        'This is a test message',
        'admin@bhrikutimandap.com',
        ['admin@bhrikutimandap.com'],
        fail_silently=False
    )
    print(f"Result: {result}")
    print(f"Emails in outbox: {len(mail.outbox)}")
    
    if len(mail.outbox) > 0:
        print(f"Email sent to: {mail.outbox[0].to}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
