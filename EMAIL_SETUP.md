# Email Configuration Guide

## Setup Instructions

### 1. Environment Variables (.env file)

The `.env` file in the project root contains all email configuration. Update it with your Hostinger credentials:

```
EMAIL_HOST=smtp.hostinger.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=admin@bhrikutimandap.com
EMAIL_HOST_PASSWORD=your-hostinger-password
DEFAULT_FROM_EMAIL=admin@bhrikutimandap.com
CONTACT_EMAIL=admin@bhrikutimandap.com
```

### 2. Local Development Setup

For **local development** (DEBUG=True):
- The email backend is set to console output
- Emails will be printed to the console/terminal instead of being sent
- This allows you to test email functionality without actual email setup

To enable actual email sending in development:
- Set `DJANGO_DEBUG=False` in `.env`
- Add your Hostinger password to `EMAIL_HOST_PASSWORD`
- Restart your Django server

### 3. Features Configured

#### Account Creation Email
When users register:
1. An account is created as inactive
2. An activation email is sent to their email address with an activation link
3. Users click the link to activate their account
4. If email fails, the account is auto-activated (fallback)

#### Contact Form Email
When users submit the contact form:
1. The message is sent to `CONTACT_EMAIL` (admin@bhrikutimandap.com)
2. The email includes: name, sender's email, subject, and message
3. Admin can reply directly to the sender's email

### 4. Testing Emails Locally

#### Method 1: Console Output (Default)
```bash
# In your terminal where Django is running, you'll see email output like:
# ------------------- EMAIL MESSAGE -------------------
# From: no-reply@bhrikutimandap.com
# To: ['user@example.com']
# Subject: Activate your account
# -------------------------------------------------------
```

#### Method 2: Local SMTP Server (MailHog)
Install and run MailHog for a visual email inbox:

```bash
# Download from: https://github.com/mailhog/MailHog/releases
# Or install via Chocolatey (Windows):
choco install mailhog

# Run MailHog
mailhog

# In .env, set:
EMAIL_HOST=localhost
EMAIL_PORT=1025

# Visit: http://localhost:8025 to see emails
```

### 5. Production Setup

For production on Hostinger:
1. Get your Hostinger SMTP credentials from hosting control panel
2. Set `DJANGO_DEBUG=False` in `.env`
3. Configure email environment variables:
   ```
   EMAIL_HOST=smtp.hostinger.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=admin@bhrikutimandap.com
   EMAIL_HOST_PASSWORD=actual-password
   ```
4. Test sending an email before going live

### 6. Troubleshooting

| Issue | Solution |
|-------|----------|
| Emails not sent in dev | Make sure DEBUG=True (console backend) or set DEBUG=False to use SMTP |
| "SMTP error" | Check EMAIL_HOST_PASSWORD is correct |
| "Connection refused" | Verify EMAIL_HOST and EMAIL_PORT are correct |
| "TLS required" | Make sure EMAIL_USE_TLS=True |
| Emails in spam folder | Ask admin to whitelist sender domain in Hostinger |

### 7. Files Modified

- `.env` - Email configuration (create this file if not present)
- `market/settings.py` - Added `CONTACT_EMAIL` setting
- `store/views.py` - Updated `contact_view()` to send emails
- Registration email in `register_view()` already sends activation emails

