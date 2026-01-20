#!/usr/bin/env python
"""Test contact form with explicit module reloading"""
import os
import sys
import django

# Clear any cached modules
if 'store' in sys.modules:
    del sys.modules['store']
if 'store.views' in sys.modules:
    del sys.modules['store.views']

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
os.environ['DJANGO_DEBUG'] = 'True'

django.setup()

# Now import
from django.test import Client
from django.conf import settings
from store.views import contact_view

# Force reimport
import importlib
import store.views
importlib.reload(store.views)

if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

print("=" * 70)
print("CONTACT FORM TEST - WITH MODULE RELOAD")
print("=" * 70)

# Create fresh client
client = Client()

contact_data = {
    'name': 'Alice Smith',
    'email': 'alice@test.com',
    'phone': '555-8765',
    'subject': 'Product inquiry',
    'message': 'Please tell me about your products'
}

print("\nForm data:")
for k, v in contact_data.items():
    print(f"  {k}: {v}")

print("\nSubmitting form...")
try:
    response = client.post('/contact/', contact_data, follow=True)
    print(f"Response: {response.status_code}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
