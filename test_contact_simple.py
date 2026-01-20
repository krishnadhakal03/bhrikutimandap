#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
django.setup()

from django.test import Client
from django.core import mail

# Create client with server_name
client = Client(enforce_csrf_checks=False, SERVER_NAME='localhost')

print("=== Testing Contact Form ===")

# Reset mail outbox
mail.outbox = []

# Try contact form
contact_data = {
    'name': 'Test User',
    'email': 'testuser@example.com',
    'phone': '1234567890',
    'subject': 'Test Subject',
    'message': 'This is a test message from the contact form.'
}

response = client.post('/contact/', contact_data, follow=True, SERVER_NAME='localhost')
print(f"Status: {response.status_code}")

if len(mail.outbox) > 0:
    email = mail.outbox[0]
    print(f"[OK] Email sent!")
    print(f"To: {email.to}")
    print(f"Subject: {email.subject}")
    print(f"From: {email.from_email}")
else:
    print("[ERROR] No email sent")

print(f"\nEmails in outbox: {len(mail.outbox)}")
