#!/usr/bin/env python
import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
os.environ['DJANGO_DEBUG'] = 'True'

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

django.setup()

from django.test import Client
from django.conf import settings
from store.views import contact_view, _get_email_connection, _get_from_email, _send_email
from store.models import EmailTemplate, SiteSettings

# Add testserver to ALLOWED_HOSTS temporarily
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

print("=" * 70)
print("TESTING CONTACT FORM EMAIL DETAILS")
print("=" * 70)

# Check SiteSettings
print("\n1. SiteSettings Check:")
try:
    site_settings = SiteSettings.get_instance()
    print(f"   Contact email: {site_settings.contact_email}")
    print(f"   Email host: {site_settings.email_host}")
    print(f"   From email: {site_settings.default_from_email}")
except Exception as e:
    print(f"   ERROR: {e}")

# Check email templates
print("\n2. Email Templates Check:")
try:
    admin_template = EmailTemplate.objects.get(name='contact_admin')
    print(f"   Admin template: {admin_template.name}")
    print(f"   Subject: {admin_template.subject}")
    
    conf_template = EmailTemplate.objects.get(name='contact_confirmation')
    print(f"   Confirmation template: {conf_template.name}")
    print(f"   Subject: {conf_template.subject}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test email sending directly
print("\n3. Test Direct Email Sending:")
try:
    from_email = _get_from_email()
    print(f"   From email: {from_email}")
    
    # Test to admin email
    test_email_to_admin = site_settings.contact_email or 'admin@example.com'
    print(f"   Sending test to: {test_email_to_admin}")
    
    result = _send_email(
        "Test Subject",
        "Test body",
        from_email,
        [test_email_to_admin],
        fail_silently=False  # Don't fail silently to see the error
    )
    print(f"   Result: {result}")
    print("   ✓ Email sent successfully")
except Exception as e:
    print(f"   ✗ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Now test the contact form
print("\n4. Testing Contact Form Submission:")
print("-" * 70)

client = Client()

contact_data = {
    'name': 'Test User',
    'email': 'testuser@example.com',
    'phone': '9876543210',
    'subject': 'Test Question',
    'message': 'Test message'
}

try:
    response = client.post('/contact/', contact_data, follow=True)
    print(f"   Response status: {response.status_code}")
    
    response_content = str(response.content)
    if 'Thanks for contacting us' in response_content:
        print("   ✓ SUCCESS: Contact form submitted successfully")
    elif 'Failed to process' in response_content:
        print("   ✗ FAILURE: Form processing failed")
    
except Exception as e:
    print(f"   ✗ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
