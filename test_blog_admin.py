#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import django

# Fix encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
os.environ['DEBUG'] = 'True'
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

# Create a test client
client = Client()

# Try to login (create superuser if needed)
try:
    user = User.objects.get(username='admin')
except User.DoesNotExist:
    user = User.objects.create_superuser('admin', 'admin@test.com', 'password123')
    print("[OK] Created test superuser")

# Login
logged_in = client.login(username='admin', password='password123')
print(f'[OK] Logged in: {logged_in}')

# Access the blog add page
response = client.get('/admin/store/blog/add/')
print(f'[OK] Response status: {response.status_code}')

if response.status_code == 200:
    print('[OK] Blog add page loaded successfully!')
    # Check for the CKEditor in the response
    if 'ckeditor' in response.content.decode().lower():
        print('[OK] CKEditor found in page')
    else:
        print('[WARN] CKEditor not found in page')
elif response.status_code == 500:
    print(f'[ERROR] Server error 500')
    print(f'Content preview: {response.content.decode()[:500]}')
else:
    print(f'Response: {response.status_code}')
    print(f'Content preview: {response.content.decode()[:500]}')
