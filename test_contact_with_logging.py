#!/usr/bin/env python
import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
os.environ['DJANGO_DEBUG'] = 'True'

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s'
)

django.setup()

from django.test import Client
from django.conf import settings

if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

# Import after Django setup
from store.views import _get_email_template, _get_from_email
from store.models import SiteSettings

print("=" * 70)
print("DETAILED CONTACT FORM TEST WITH LOGGING")
print("=" * 70)

print("\n1. Pre-flight checks:")
print(f"   From email: {_get_from_email()}")
print(f"   Contact email (SiteSettings): {SiteSettings.get_instance().contact_email}")

template = _get_email_template('contact_admin')
print(f"   Contact admin template: {template}")
if template:
    print(f"     Subject: {template.subject}")
    print(f"     Is active: {template.is_active}")

print("\n2. Submitting contact form...")
client = Client()

contact_data = {
    'name': 'Test User',
    'email': 'testuser@example.com',
    'phone': '9876543210',
    'subject': 'Test Question',
    'message': 'Test message body'
}

try:
    response = client.post('/contact/', contact_data, follow=True)
    print(f"   Response status: {response.status_code}")
    
    content = str(response.content)
    if 'Thanks for contacting us' in content:
        print("   ✓ SUCCESS message found")
    else:
        print("   ✗ SUCCESS message NOT found")
        if 'Failed to process' in content:
            print("   ✗ FAILURE message found")
        
except Exception as e:
    print(f"   ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
