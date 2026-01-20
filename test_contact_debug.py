#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
os.environ['DJANGO_DEBUG'] = 'True'
django.setup()

from django.test import Client
from django.conf import settings

# Add testserver to ALLOWED_HOSTS temporarily
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

print("=" * 70)
print("TESTING CONTACT FORM DETAILED")
print("=" * 70)

client = Client()

contact_data = {
    'name': 'Test User',
    'email': 'testuser@example.com',
    'phone': '9876543210',
    'subject': 'Test Question About Products',
    'message': 'I would like to know more about your products.'
}

print("\nAttempting to submit contact form...")
print(f"Data: {contact_data}")

try:
    response = client.post('/contact/', contact_data, follow=True)
    print(f"\nResponse status: {response.status_code}")
    
    # Check the response content for messages
    response_content = str(response.content)
    
    if 'Thanks for contacting us' in response_content:
        print("✓ SUCCESS MESSAGE FOUND")
    elif 'Failed to send message' in response_content:
        print("✗ FAILURE MESSAGE FOUND")
    
    # Look for error details in response
    if 'email' in response_content.lower():
        print("Email-related content detected in response")
    
    print("\nResponse content (first 2000 chars):")
    print(response_content[:2000])
    
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
