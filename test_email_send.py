#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
django.setup()

from store.models import SiteSettings
from django.core.mail import send_mail, get_connection
from store.views import _get_email_connection, _send_email

# Update SiteSettings with password
print("=== Updating SiteSettings ===")
site_settings = SiteSettings.get_instance()
site_settings.email_host_password = 'Bhrikutimandap@2026$$$$'
site_settings.save()
print(f"[OK] Updated password in SiteSettings")

# Test SMTP connection
print("\n=== Testing SMTP Connection ===")
try:
    conn = _get_email_connection()
    if conn:
        # Try to open connection
        conn.open()
        conn.close()
        print("[OK] SMTP connection successful!")
    else:
        print("[ERROR] Could not create connection")
except Exception as e:
    print(f"[ERROR] Connection failed: {e}")

# Test send email
print("\n=== Testing Email Send (Contact Us) ===")
try:
    subject = "Test Email - Contact Us"
    message = "This is a test email from the contact form to verify SMTP is working."
    from_email = "admin@bhrikutimandap.com"
    recipient_list = ["admin@bhrikutimandap.com"]  # Send to same email
    
    result = _send_email(subject, message, from_email, recipient_list, fail_silently=False)
    print(f"[OK] Test email sent successfully! (Result: {result})")
except Exception as e:
    print(f"[ERROR] Failed to send email: {e}")
    import traceback
    traceback.print_exc()

# Test registration email (check what gets sent)
print("\n=== Checking Registration Email Flow ===")
try:
    from django.contrib.auth import get_user_model
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.encoding import force_bytes
    from django.utils.http import urlsafe_base64_encode
    
    User = get_user_model()
    test_user = User(username='emailtest', email='admin@bhrikutimandap.com')
    
    uid = urlsafe_base64_encode(force_bytes(test_user.pk))
    token = default_token_generator.make_token(test_user)
    
    print(f"[OK] Registration email would send to: {test_user.email}")
    print(f"[OK] Activation token can be generated: {token[:20]}...")
except Exception as e:
    print(f"[ERROR] Registration flow check failed: {e}")
