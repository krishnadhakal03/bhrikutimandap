#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
django.setup()

from store.models import EmailTemplate, SiteSettings
from store.views import _get_email_template, _get_from_email, _send_email

print("=" * 60)
print("TESTING EMAIL TEMPLATES")
print("=" * 60)

# Test 1: Check templates exist
print("\n1. EmailTemplate count:", EmailTemplate.objects.count())
for t in EmailTemplate.objects.all():
    print(f"   - {t.name} ({t.template_type})")

# Test 2: Check SiteSettings
print("\n2. SiteSettings check:")
try:
    site_settings = SiteSettings.get_instance()
    print(f"   Email host: {site_settings.email_host}")
    print(f"   Email port: {site_settings.email_port}")
    print(f"   Email user: {site_settings.email_host_user}")
    print(f"   Email use TLS: {site_settings.email_use_tls}")
    print(f"   From email: {site_settings.default_from_email}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 3: Test contact_admin template rendering
print("\n3. Test contact_admin template rendering:")
try:
    template = _get_email_template('contact_admin')
    if template:
        print(f"   Template found: {template.name}")
        print(f"   Subject template: {template.subject}")
        subject = template.subject.format(subject_input="Test Question")
        print(f"   Rendered subject: {subject}")
        
        body = template.render(
            name="John Doe",
            email="john@example.com",
            phone="9876543210",
            subject_input="Test Question",
            message="This is a test message"
        )
        print(f"   Body preview (first 200 chars):\n   {body[:200]}...")
    else:
        print("   ERROR: contact_admin template not found!")
except Exception as e:
    print(f"   ERROR rendering: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Test contact_confirmation template rendering
print("\n4. Test contact_confirmation template rendering:")
try:
    template = _get_email_template('contact_confirmation')
    if template:
        print(f"   Template found: {template.name}")
        print(f"   Subject: {template.subject}")
        
        body = template.render(
            name="John Doe",
            subject_input="Test Question",
            date="2026-01-19 10:00:00"
        )
        print(f"   Body preview (first 200 chars):\n   {body[:200]}...")
    else:
        print("   ERROR: contact_confirmation template not found!")
except Exception as e:
    print(f"   ERROR rendering: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Test password_reset template
print("\n5. Test password_reset template rendering:")
try:
    template = _get_email_template('password_reset')
    if template:
        print(f"   Template found: {template.name}")
        print(f"   Subject: {template.subject}")
        
        body = template.render(
            username="testuser",
            email="test@example.com",
            reset_link="https://www.bhrikutimandap.com/accounts/password-reset/confirm/abc123/token123/"
        )
        print(f"   Body preview (first 200 chars):\n   {body[:200]}...")
    else:
        print("   ERROR: password_reset template not found!")
except Exception as e:
    print(f"   ERROR rendering: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Test email sending (without actually sending)
print("\n6. Test email configuration:")
print(f"   From email: {_get_from_email()}")
try:
    from django.conf import settings
    print(f"   DEBUG: {settings.DEBUG}")
    print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 60)
