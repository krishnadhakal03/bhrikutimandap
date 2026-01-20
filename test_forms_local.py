#!/usr/bin/env python
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
os.environ['DJANGO_DEBUG'] = 'True'  # Set DEBUG=True for testing
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.conf import settings

User = get_user_model()

# Add testserver to ALLOWED_HOSTS temporarily
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

print("=" * 70)
print("TESTING CONTACT FORM AND PASSWORD RESET")
print("=" * 70)

# Test 1: Test contact form POST
print("\n1. Testing Contact Form Submission:")
print("-" * 70)

client = Client()

contact_data = {
    'name': 'Test User',
    'email': 'testuser@example.com',
    'phone': '9876543210',
    'subject': 'Test Question About Products',
    'message': 'I would like to know more about your products.'
}

try:
    response = client.post('/contact/', contact_data, follow=True)
    print(f"   Response status: {response.status_code}")
    if response.status_code == 200:
        print("   ✓ Form submitted successfully (200 OK)")
        # Check for success message
        if 'Thanks for contacting us' in str(response.content):
            print("   ✓ Success message found in response")
        else:
            print("   ✗ Success message NOT found in response")
    else:
        print(f"   ✗ Unexpected status: {response.status_code}")
        print(f"   Response content (first 500 chars):\n   {str(response.content)[:500]}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Test password reset page load
print("\n2. Testing Password Reset Page Load:")
print("-" * 70)

try:
    response = client.get('/accounts/password-reset/')
    print(f"   Response status: {response.status_code}")
    if response.status_code == 200:
        print("   ✓ Password reset page loads successfully")
    else:
        print(f"   ✗ Unexpected status: {response.status_code}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Create a test user and test password reset form
print("\n3. Testing Password Reset Form Submission:")
print("-" * 70)

# Create or get test user
try:
    user = User.objects.get(username='testpassreset')
    print(f"   Using existing test user: {user.email}")
except User.DoesNotExist:
    user = User.objects.create_user(
        username='testpassreset',
        email='testuser@example.com',
        password='testpass123'
    )
    print(f"   Created test user: {user.email}")

try:
    reset_data = {
        'email': user.email
    }
    response = client.post('/accounts/password-reset/', reset_data, follow=True)
    print(f"   Response status: {response.status_code}")
    if response.status_code == 200:
        print("   ✓ Password reset form submitted successfully")
    else:
        print(f"   ✗ Unexpected status: {response.status_code}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("TESTING COMPLETE")
print("=" * 70)
