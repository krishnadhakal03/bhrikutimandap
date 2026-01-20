#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
django.setup()

from store.models import EmailTemplate

templates_data = [
    {
        'name': 'activation',
        'template_type': 'activation',
        'subject': 'Welcome to Bhrikutimandap - Activate Your Account',
        'body': """Welcome to Bhrikutimandap!

Hello {username},

Thank you for registering with us. To activate your account, please click the link below:

{activation_link}

User Details:
Username: {username}
User ID: {user_id}
Email: {email}

This activation link will expire in 24 hours.

If you did not create this account, please ignore this email.

Best regards,
Bhrikutimandap Team"""
    },
    {
        'name': 'contact_admin',
        'template_type': 'contact_admin',
        'subject': 'Contact Form Submission: {subject_input}',
        'body': """New Contact Form Submission

Name: {name}
Email: {email}
Phone: {phone}
Subject: {subject_input}

Message:
{message}"""
    },
    {
        'name': 'contact_confirmation',
        'template_type': 'contact_admin',
        'subject': 'We received your message',
        'body': """Hello {name},

Thank you for contacting Bhrikutimandap!

We have received your email and appreciate you reaching out to us. Our team will review your message and get back to you shortly.

Your Message Details:
Subject: {subject_input}
Date: {date}

We typically respond within 24-48 hours.

Best regards,
Bhrikutimandap Team"""
    },
    {
        'name': 'welcome',
        'template_type': 'welcome',
        'subject': 'Welcome to Bhrikutimandap!',
        'body': """Hello {username},

Welcome to Bhrikutimandap!

Your account has been successfully created. You can now log in and explore our services.

Username: {username}
Email: {email}

If you have any questions, feel free to contact us.

Best regards,
Bhrikutimandap Team"""
    },
    {
        'name': 'password_reset',
        'template_type': 'password_reset',
        'subject': 'Password Reset Request for Your Bhrikutimandap Account',
        'body': """Hello {username},

We received a request to reset the password for your Bhrikutimandap account.

Please click the link below to reset your password:

{reset_link}

This link will expire in 24 hours.

If you did not request this password reset, please ignore this email or contact us immediately.

Best regards,
Bhrikutimandap Team"""
    }
]

for template_data in templates_data:
    template, created = EmailTemplate.objects.get_or_create(
        name=template_data['name'],
        defaults=template_data
    )
    if created:
        print(f"[OK] Created template: {template.name}")
    else:
        print(f"[EXIST] Template already exists: {template.name}")

print("\n=== Available Email Templates ===")
templates = EmailTemplate.objects.all()
for template in templates:
    print(f"- {template.name}: {template.get_template_type_display()}")
