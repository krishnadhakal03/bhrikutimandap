from django.core.management.base import BaseCommand
from store.models import EmailTemplate


class Command(BaseCommand):
    help = 'Seed all email templates including OTP verification'

    def handle(self, *args, **options):
        # OTP Verification Template (Professional HTML)
        otp_body_html = """
<div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
    <!-- Header with Logo -->
    <div style="background-color: #f8f9fa; padding: 30px; text-align: center; border-bottom: 1px solid #eee;">
        <img src="{logo_url}" alt="{site_title}" style="max-height: 150px; width: auto; display: block; margin: 0 auto;" />
    </div>
    
    <!-- Body Content -->
    <div style="padding: 40px 30px; text-align: center;">
        <h2 style="color: #333; margin-top: 0; font-weight: 600;">Verification Required</h2>
        <p style="color: #666; font-size: 16px; line-height: 1.5; margin-bottom: 30px;">
            Hello <strong>{username}</strong>,<br>
            Use the One-Time Password (OTP) below to verify your account.
        </p>
        
        <!-- OTP Box -->
        <div style="background-color: #e8f0fe; color: #1a73e8; font-size: 32px; font-weight: bold; letter-spacing: 5px; padding: 20px; border-radius: 8px; display: inline-block; margin-bottom: 30px; border: 1px dashed #1a73e8;">
            {otp}
        </div>
        
        <p style="color: #999; font-size: 14px; margin-top: 0;">
            This verification code is valid for <strong>10 minutes</strong>.
        </p>
        
        <p style="color: #999; font-size: 14px; margin-top: 20px; font-style: italic;">
            If you did not request this registration, please ignore this email.
        </p>
    </div>
    
    <!-- Footer -->
    <div style="background-color: #f8f9fa; padding: 20px; text-align: center; color: #999; font-size: 12px; border-top: 1px solid #eee;">
        &copy; {site_title}. All rights reserved.
    </div>
</div>
"""

        templates_data = [
            {
                'name': 'otp_verification',
                'template_type': 'otp_verification',
                'subject': 'Verify your account - {username}',
                'body': otp_body_html.strip(),
                'is_active': True
            },
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
Bhrikutimandap Team""",
                'is_active': True
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
{message}""",
                'is_active': True
            },
            {
                'name': 'contact_confirmation',
                'template_type': 'contact_confirmation',
                'subject': 'We received your message',
                'body': """Hello {name},

Thank you for contacting Bhrikutimandap!

We have received your email and appreciate you reaching out to us. Our team will review your message and get back to you shortly.

Your Message Details:
Subject: {subject_input}
Date: {date}

We typically respond within 24-48 hours.

Best regards,
Bhrikutimandap Team""",
                'is_active': True
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
Bhrikutimandap Team""",
                'is_active': True
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
Bhrikutimandap Team""",
                'is_active': True
            }
        ]

        created_count = 0
        updated_count = 0
        
        for template_data in templates_data:
            template, created = EmailTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {template.name}')
                )
                created_count += 1
            else:
                # Update existing template to ensure latest version
                template.template_type = template_data['template_type']
                template.subject = template_data['subject']
                template.body = template_data['body']
                template.is_active = template_data.get('is_active', True)
                template.save()
                self.stdout.write(
                    self.style.WARNING(f'✓ Updated: {template.name}')
                )
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Email templates seeded successfully!'
                f'\n  - Created: {created_count}'
                f'\n  - Updated: {updated_count}'
                f'\n  - Total: {created_count + updated_count}'
            )
        )
