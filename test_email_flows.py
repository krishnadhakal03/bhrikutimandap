#!/usr/bin/env python
import os
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.core import mail
from django.middleware.csrf import get_token

User = get_user_model()
client = Client(enforce_csrf_checks=False)

print("\n" + "="*60)
print("TEST 1: CONTACT FORM SUBMISSION")
print("="*60)

# Reset mail outbox
mail.outbox = []

# Test contact form submission
contact_data = {
    'name': 'Test User',
    'email': 'testuser@example.com',
    'phone': '1234567890',
    'subject': 'Test Subject',
    'message': 'This is a test message from the contact form.'
}

response = client.post('/contact/', contact_data)
print(f"[1] Form submission status: {response.status_code}")

if response.status_code == 200:
    # Check if email was sent
    if len(mail.outbox) > 0:
        email = mail.outbox[0]
        print(f"[2] Email sent to: {email.to}")
        print(f"[3] Email subject: {email.subject}")
        print(f"[4] Email from: {email.from_email}")
        print(f"[5] Email body preview: {email.body[:150]}...")
        print("[OK] Contact form email test PASSED")
    else:
        print("[ERROR] No email sent from contact form")
else:
    print(f"[ERROR] Form submission failed with status {response.status_code}")

print("\n" + "="*60)
print("TEST 2: USER REGISTRATION WITH EMAIL VERIFICATION")
print("="*60)

# Reset mail outbox
mail.outbox = []

# Delete test user if exists
User.objects.filter(username='testreguser').delete()

# Register new user
register_data = {
    'username': 'testreguser',
    'email': 'testreg@example.com',
    'password1': 'TestPass123!@#',
    'password2': 'TestPass123!@#',
}

response = client.post('/accounts/register/', register_data)
print(f"[1] Registration status: {response.status_code}")

# Check if user was created (but not activated yet)
try:
    user = User.objects.get(username='testreguser')
    print(f"[2] User created: {user.username}")
    print(f"[3] User is active: {user.is_active}")
    
    # Check activation email
    if len(mail.outbox) > 0:
        activation_email = mail.outbox[0]
        print(f"[4] Activation email sent to: {activation_email.to}")
        print(f"[5] Email subject: {activation_email.subject}")
        print(f"[6] Email body preview: {activation_email.body[:200]}...")
        
        if 'activate' in activation_email.body.lower():
            print("[OK] User registration email test PASSED")
        else:
            print("[WARN] Activation link not found in email")
    else:
        print("[ERROR] No activation email sent")
        
except User.DoesNotExist:
    print("[ERROR] User was not created")

print("\n" + "="*60)
print("TEST 3: PASSWORD RESET EMAIL")
print("="*60)

# Reset mail outbox
mail.outbox = []

# Create a test user for password reset
test_user, _ = User.objects.get_or_create(
    username='passwordresettest',
    defaults={'email': 'pwreset@example.com', 'is_active': True}
)

# Request password reset
reset_data = {'email': 'pwreset@example.com'}
response = client.post('/accounts/password-reset/', reset_data)
print(f"[1] Password reset request status: {response.status_code}")

if len(mail.outbox) > 0:
    reset_email = mail.outbox[0]
    print(f"[2] Reset email sent to: {reset_email.to}")
    print(f"[3] Email subject: {reset_email.subject}")
    print(f"[4] Email body preview: {reset_email.body[:200]}...")
    
    if 'reset' in reset_email.body.lower() or 'confirm' in reset_email.body.lower():
        print("[OK] Password reset email test PASSED")
    else:
        print("[WARN] Reset link not clearly in email")
else:
    print("[ERROR] No password reset email sent")

print("\n" + "="*60)
print("SUMMARY: ALL EMAIL FLOWS TESTED")
print("="*60)
