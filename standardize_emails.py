import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
django.setup()

from store.models import EmailTemplate

# The "Master" Design (from OTP template)
# We replace the specific content area with a placeholder {content_body}
MASTER_TEMPLATE = """
<div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
    <!-- Header with Logo -->
    <div style="background-color: #f8f9fa; padding: 30px; text-align: center; border-bottom: 1px solid #eee;">
        <img src="{logo_url}" alt="{site_title}" style="max-height: 150px; width: auto; display: block; margin: 0 auto;" />
    </div>
    
    <!-- Body Content -->
    <div style="padding: 40px 30px; text-align: center;">
        {content_body}
    </div>
    
    <!-- Footer -->
    <div style="background-color: #f8f9fa; padding: 20px; text-align: center; color: #999; font-size: 12px; border-top: 1px solid #eee;">
        &copy; {site_title}. All rights reserved.
    </div>
</div>
"""

def update_templates():
    templates_to_update = {
        'activation': {
            'subject': 'Activate your {site_title} Account',
            'content_body': """
                <h2 style="color: #333; margin-top: 0; font-weight: 600;">Welcome, {username}!</h2>
                <p style="color: #666; font-size: 16px; line-height: 1.5; margin-bottom: 30px;">
                    Thank you for registering. Please activate your account to get started.
                </p>
                <div style="margin-bottom: 30px;">
                    <a href="{activation_link}" style="background-color: #1a73e8; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">Activate Account</a>
                </div>
                <p style="color: #999; font-size: 14px; margin-top: 20px;">
                    Or copy this link: <br>
                    <a href="{activation_link}" style="color: #1a73e8;">{activation_link}</a>
                </p>
            """
        },
        'welcome': {
            'subject': 'Welcome to {site_title}, {username}!',
            'content_body': """
                <h2 style="color: #333; margin-top: 0; font-weight: 600;">Welcome to the Family!</h2>
                <p style="color: #666; font-size: 16px; line-height: 1.5; margin-bottom: 30px;">
                    We are thrilled to have you on board, <strong>{username}</strong>. 
                    Explore our collection of premium local products.
                </p>
                <div style="margin-bottom: 30px;">
                    <a href="{site_url}" style="background-color: #1a73e8; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">Start Shopping</a>
                </div>
            """
        },
        'password_reset': {
            'subject': 'Reset Your Password - {site_title}',
            'content_body': """
                <h2 style="color: #333; margin-top: 0; font-weight: 600;">Password Reset Request</h2>
                <p style="color: #666; font-size: 16px; line-height: 1.5; margin-bottom: 30px;">
                    Hello {username},<br>
                    We received a request to reset your password. Click the button below to proceed.
                </p>
                <div style="margin-bottom: 30px;">
                    <a href="{reset_link}" style="background-color: #d93025; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">Reset Password</a>
                </div>
                <p style="color: #999; font-size: 14px; margin-top: 20px;">
                    If you didn't ask for this, you can safely ignore this email.
                </p>
            """
        },
        'contact_admin': {
            'subject': 'New Contact Message: {subject_input}',
            'content_body': """
                <h2 style="color: #333; margin-top: 0; font-weight: 600;">New Message Received</h2>
                <div style="text-align: left; background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
                    <p style="margin: 5px 0;"><strong>From:</strong> {name} ({email})</p>
                    <p style="margin: 5px 0;"><strong>Phone:</strong> {phone}</p>
                    <hr style="border: 0; border-top: 1px solid #ddd; margin: 15px 0;">
                    <p style="margin: 5px 0; font-style: italic;">"{message}"</p>
                </div>
                <p style="color: #666; font-size: 14px;">
                    Login to the admin panel to respond.
                </p>
            """
        }
    }

    print("--- UPDATING EMAIL TEMPLATES ---")
    for name, content in templates_to_update.items():
        # Combine master template with specific body
        full_body = MASTER_TEMPLATE.format(
            logo_url="{logo_url}", 
            site_title="{site_title}", 
            content_body=content['content_body']
        ).strip()
        
        # Create or Update
        template, created = EmailTemplate.objects.get_or_create(
            name=name,
            defaults={
                'template_type': name,
                'subject': content['subject'],
                'body': full_body,
                'is_active': True
            }
        )
        
        if not created:
            template.body = full_body
            template.subject = content['subject']
            template.save()
            print(f"[UPDATED] {name}")
        else:
            print(f"[CREATED] {name}")

    print("\n--- DONE ---")

if __name__ == '__main__':
    update_templates()
