import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
django.setup()

from store.models import SiteSettings

try:
    s = SiteSettings.get_instance()
    print(f"Host: {s.email_host}")
    print(f"Port: {s.email_port}")
    print(f"User: {s.email_host_user}")
    print(f"TLS: {s.email_use_tls}")
    print(f"Password Length: {len(s.email_host_password) if s.email_host_password else 0}")
    print(f"From Email: {s.default_from_email}")
except Exception as e:
    print(f"Error: {e}")
