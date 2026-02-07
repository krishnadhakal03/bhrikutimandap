import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
django.setup()

from store.models import SiteSettings, EmailTemplate

print("--- DEBUGGING LOGO URL ---")
try:
    site_settings = SiteSettings.get_instance()
    print(f"Site Title: {site_settings.site_title}")
    if site_settings.logo:
        print(f"Logo File: {site_settings.logo}")
        print(f"Logo URL attribute: {site_settings.logo.url}")
        
        # Simulate URL construction
        site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')
        full_url = f"{site_url}{site_settings.logo.url}"
        print(f"Constructed Full URL: {full_url}")
    else:
        print("NO LOGO FOUND in SiteSettings.")
except Exception as e:
    print(f"Error accessing SiteSettings: {e}")

print("\n--- CHECKING EMAIL TEMPLATE ---")
try:
    template = EmailTemplate.objects.get(template_type='otp_verification')
    print(f"Template Subject: {template.subject}")
    print(f"Template Body Preview (first 100 chars): {template.body[:100]}")
    if '{logo_url}' in template.body:
        print("PASS: '{logo_url}' placeholder found in template body.")
    else:
        print("FAIL: '{logo_url}' placeholder NOT found in template body.")
except EmailTemplate.DoesNotExist:
    print("FAIL: 'otp_verification' template not found.")
except Exception as e:
    print(f"Error accessing EmailTemplate: {e}")
