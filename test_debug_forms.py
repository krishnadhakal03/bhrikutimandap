#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
django.setup()

from django.test import Client

client = Client(enforce_csrf_checks=False)

# Get contact page first to see if it works
response = client.get('/contact/')
print(f"GET /contact/ status: {response.status_code}")

# Try simple contact form POST
contact_data = {
    'name': 'Test User',
    'email': 'testuser@example.com',
    'phone': '1234567890',
    'subject': 'Test Subject',
    'message': 'This is a test message from the contact form.'
}

response = client.post('/contact/', contact_data, follow=True)
print(f"POST /contact/ status: {response.status_code}")

if response.status_code != 200:
    print(f"Response content: {response.content.decode()[:500]}")

# Check registration page
response = client.get('/accounts/register/')
print(f"GET /accounts/register/ status: {response.status_code}")

# Try registration
register_data = {
    'username': 'testreguser',
    'email': 'testreg@example.com',
    'password1': 'TestPass123!@#',
    'password2': 'TestPass123!@#',
}

response = client.post('/accounts/register/', register_data, follow=True)
print(f"POST /accounts/register/ status: {response.status_code}")

if response.status_code != 200:
    print(f"Response content: {response.content.decode()[:500]}")
