#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
django.setup()

from store.views import _get_email_template
from store.models import EmailTemplate

print("Checking email templates...")
print(f"Total templates: {EmailTemplate.objects.count()}")
for t in EmailTemplate.objects.all():
    print(f"  - {t.name} (is_active={t.is_active})")

print("\nTesting _get_email_template()...")
templates_to_test = ['contact_admin', 'contact_confirmation', 'password_reset', 'activation']
for name in templates_to_test:
    template = _get_email_template(name)
    print(f"  {name}: {template}")
    if template:
        print(f"    Subject: {template.subject}")

print("\nDirect query test...")
try:
    template = EmailTemplate.objects.get(name='contact_admin', is_active=True)
    print(f"Found: {template}")
except Exception as e:
    print(f"Not found: {e}")
