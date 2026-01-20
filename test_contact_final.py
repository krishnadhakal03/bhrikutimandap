#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
os.environ['DJANGO_DEBUG'] = 'True'
django.setup()

from django.test import Client
from django.conf import settings

if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

print("=" * 70)
print("TESTING CONTACT FORM - FINAL TEST")
print("=" * 70)

client = Client()

contact_data = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'phone': '5551234567',
    'subject': 'Question about products',
    'message': 'I would like more information about your products.'
}

print("\nSubmitting contact form...")
print(f"Name: {contact_data['name']}")
print(f"Email: {contact_data['email']}")
print(f"Subject: {contact_data['subject']}")

try:
    response = client.post('/contact/', contact_data, follow=True)
    print(f"\n✓ Response status: {response.status_code}")
    
    content = str(response.content)
    
    # Check for success/failure messages
    if 'Thanks for contacting us' in content:
        print("✓ SUCCESS MESSAGE: 'Thanks for contacting us. We will reply soon.'")
    elif 'Failed to send message' in content:
        print("✗ FAILED MESSAGE: 'Failed to send message'")
    elif 'Failed to process' in content:
        print("✗ FAILED MESSAGE: 'Failed to process your message'")
    else:
        print("? Unknown response (check output below)")
    
    # Look for Django messages in the response
    if 'messages' in content:
        print("\nMessages section found in response")
        
except Exception as e:
    print(f"\n✗ EXCEPTION: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
