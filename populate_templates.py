import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
django.setup()

from store.models import EmailTemplate

# Professional, branded HTML template for OTP
otp_template_name = 'otp_verification'
otp_subject = 'Verify your account - {username}'

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

# Create or Update the template
template, created = EmailTemplate.objects.get_or_create(
    name=otp_template_name,
    defaults={
        'template_type': 'otp_verification',
        'subject': otp_subject,
        'body': otp_body_html.strip(),
        'is_active': True
    }
)

if not created:
    # Optional: Update existing template to the new design
    # Comment this out if you don't want to overwrite existing changes
    template.template_type = 'otp_verification'
    template.subject = otp_subject
    template.body = otp_body_html.strip()
    template.save()
    print(f"Updated existing template: {template}")
else:
    print(f"Created new template: {template}")
