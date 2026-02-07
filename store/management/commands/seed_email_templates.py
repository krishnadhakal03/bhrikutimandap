from django.core.management.base import BaseCommand
from store.models import EmailTemplate


class Command(BaseCommand):
    help = 'Seed all email templates including OTP verification'

    def handle(self, *args, **options):
        # Base HTML template structure for consistency
        def create_html_template(title, content, show_logo=True):
            logo_section = """
    <!-- Header with Logo -->
    <div style="background-color: #f8f9fa; padding: 30px; text-align: center; border-bottom: 1px solid #eee;">
        <img src="{logo_url}" alt="{site_title}" style="max-height: 150px; width: auto; display: block; margin: 0 auto;" />
    </div>
""" if show_logo else ""
            
            return f"""
<div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
{logo_section}
    <!-- Body Content -->
    <div style="padding: 40px 30px;">
        <h2 style="color: #333; margin-top: 0; font-weight: 600; text-align: center;">{title}</h2>
{content}
    </div>
    
    <!-- Footer -->
    <div style="background-color: #f8f9fa; padding: 20px; text-align: center; color: #999; font-size: 12px; border-top: 1px solid #eee;">
        &copy; {{site_title}}. All rights reserved.
    </div>
</div>
"""

        templates_data = [
            {
                'name': 'otp_verification',
                'template_type': 'otp_verification',
                'subject': 'Verify your account - {username}',
                'body': create_html_template(
                    'Verification Required',
                    """
        <p style="color: #666; font-size: 16px; line-height: 1.5; margin-bottom: 30px; text-align: center;">
            Hello <strong>{username}</strong>,<br>
            Use the One-Time Password (OTP) below to verify your account.
        </p>
        
        <!-- OTP Box -->
        <div style="text-align: center;">
            <div style="background-color: #e8f0fe; color: #1a73e8; font-size: 32px; font-weight: bold; letter-spacing: 5px; padding: 20px; border-radius: 8px; display: inline-block; margin-bottom: 30px; border: 1px dashed #1a73e8;">
                {otp}
            </div>
        </div>
        
        <p style="color: #999; font-size: 14px; margin-top: 0; text-align: center;">
            This verification code is valid for <strong>10 minutes</strong>.
        </p>
        
        <p style="color: #999; font-size: 14px; margin-top: 20px; font-style: italic; text-align: center;">
            If you did not request this registration, please ignore this email.
        </p>
"""
                ),
                'is_active': True
            },
            {
                'name': 'activation',
                'template_type': 'activation',
                'subject': 'Welcome to {site_title} - Activate Your Account',
                'body': create_html_template(
                    'Welcome to {site_title}!',
                    """
        <p style="color: #666; font-size: 16px; line-height: 1.5; margin-bottom: 20px;">
            Hello <strong>{username}</strong>,
        </p>
        
        <p style="color: #666; font-size: 16px; line-height: 1.5; margin-bottom: 30px;">
            Thank you for registering with us. To activate your account, please click the button below:
        </p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{activation_link}" style="background-color: #667eea; color: white; padding: 14px 30px; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);">
                Activate Account
            </a>
        </div>
        
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 5px 0; color: #666; font-size: 14px;"><strong>Username:</strong> {username}</p>
            <p style="margin: 5px 0; color: #666; font-size: 14px;"><strong>Email:</strong> {email}</p>
        </div>
        
        <p style="color: #999; font-size: 13px; margin-top: 20px; font-style: italic;">
            This activation link will expire in 24 hours. If you did not create this account, please ignore this email.
        </p>
"""
                ),
                'is_active': True
            },
            {
                'name': 'password_reset',
                'template_type': 'password_reset',
                'subject': 'Password Reset Request for Your {site_title} Account',
                'body': create_html_template(
                    'Password Reset Request',
                    """
        <p style="color: #666; font-size: 16px; line-height: 1.5; margin-bottom: 20px;">
            Hello <strong>{username}</strong>,
        </p>
        
        <p style="color: #666; font-size: 16px; line-height: 1.5; margin-bottom: 30px;">
            We received a request to reset the password for your account. Click the button below to create a new password:
        </p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_link}" style="background-color: #667eea; color: white; padding: 14px 30px; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);">
                Reset Password
            </a>
        </div>
        
        <p style="color: #999; font-size: 13px; margin-top: 20px;">
            This link will expire in <strong>24 hours</strong>.
        </p>
        
        <p style="color: #999; font-size: 13px; margin-top: 20px; font-style: italic;">
            If you did not request this password reset, please ignore this email or contact us immediately.
        </p>
"""
                ),
                'is_active': True
            },
            {
                'name': 'welcome',
                'template_type': 'welcome',
                'subject': 'Welcome to {site_title}!',
                'body': create_html_template(
                    'Welcome to {site_title}!',
                    """
        <p style="color: #666; font-size: 16px; line-height: 1.5; margin-bottom: 20px;">
            Hello <strong>{username}</strong>,
        </p>
        
        <p style="color: #666; font-size: 16px; line-height: 1.5; margin-bottom: 30px;">
            Your account has been successfully created! You can now log in and explore our services.
        </p>
        
        <div style="background-color: #e8f5e9; padding: 20px; border-radius: 8px; border-left: 4px solid #4caf50; margin: 20px 0;">
            <p style="margin: 5px 0; color: #2e7d32; font-size: 14px;"><strong>✓ Account Created Successfully</strong></p>
            <p style="margin: 5px 0; color: #666; font-size: 14px;">Username: {username}</p>
            <p style="margin: 5px 0; color: #666; font-size: 14px;">Email: {email}</p>
        </div>
        
        <p style="color: #666; font-size: 16px; line-height: 1.5; margin-top: 30px;">
            If you have any questions, feel free to contact us.
        </p>
"""
                ),
                'is_active': True
            },
            {
                'name': 'contact_admin',
                'template_type': 'contact_admin',
                'subject': 'Contact Form Submission: {subject_input}',
                'body': create_html_template(
                    'New Contact Form Submission',
                    """
        <div style="background-color: #fff3cd; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107; margin-bottom: 20px;">
            <p style="margin: 0; color: #856404; font-size: 14px;"><strong>⚠ New Message Received</strong></p>
        </div>
        
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 10px 0; color: #666; font-size: 14px;"><strong>Name:</strong> {name}</p>
            <p style="margin: 10px 0; color: #666; font-size: 14px;"><strong>Email:</strong> {email}</p>
            <p style="margin: 10px 0; color: #666; font-size: 14px;"><strong>Phone:</strong> {phone}</p>
            <p style="margin: 10px 0; color: #666; font-size: 14px;"><strong>Subject:</strong> {subject_input}</p>
        </div>
        
        <div style="background-color: #ffffff; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0 0 10px 0; color: #333; font-size: 14px; font-weight: 600;">Message:</p>
            <p style="margin: 0; color: #666; font-size: 14px; line-height: 1.6; white-space: pre-wrap;">{message}</p>
        </div>
""",
                    show_logo=False  # Admin emails don't need logo
                ),
                'is_active': True
            },
            {
                'name': 'contact_confirmation',
                'template_type': 'contact_confirmation',
                'subject': 'We received your message',
                'body': create_html_template(
                    'Thank You for Contacting Us',
                    """
        <p style="color: #666; font-size: 16px; line-height: 1.5; margin-bottom: 20px;">
            Hello <strong>{name}</strong>,
        </p>
        
        <p style="color: #666; font-size: 16px; line-height: 1.5; margin-bottom: 30px;">
            Thank you for contacting {site_title}! We have received your message and appreciate you reaching out to us.
        </p>
        
        <div style="background-color: #e3f2fd; padding: 20px; border-radius: 8px; border-left: 4px solid #2196f3; margin: 20px 0;">
            <p style="margin: 5px 0; color: #1565c0; font-size: 14px;"><strong>✓ Message Received</strong></p>
            <p style="margin: 5px 0; color: #666; font-size: 14px;">Subject: {subject_input}</p>
            <p style="margin: 5px 0; color: #666; font-size: 14px;">Date: {date}</p>
        </div>
        
        <p style="color: #666; font-size: 16px; line-height: 1.5; margin-top: 30px;">
            Our team will review your message and get back to you shortly. We typically respond within 24-48 hours.
        </p>
"""
                ),
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
