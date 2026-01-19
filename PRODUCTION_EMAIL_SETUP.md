# Production Email Setup Guide

## Issue
"Failed to send message (dev)" when submitting contact form in production with Hostinger SMTP.

## Root Cause
The production environment is not reading the `.env` file correctly. This can happen if:
1. `python-dotenv` is not installed on the production server
2. `.env` file is not deployed to production
3. Environment variables need to be set at the server level instead

## Solution

### Option 1: Using Server Environment Variables (Recommended for Production)

Instead of relying on `.env` file, set environment variables directly on your Hostinger server:

**Via Hostinger Control Panel:**
1. Go to Hostinger Admin → App Management or Environment Variables
2. Set these variables:
   ```
   EMAIL_HOST=smtp.hostinger.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=admin@bhrikutimandap.com
   EMAIL_HOST_PASSWORD=Bhrikutimandap@2026$$$$
   DEFAULT_FROM_EMAIL=admin@bhrikutimandap.com
   CONTACT_EMAIL=admin@bhrikutimandap.com
   ```

**Via SSH (if available):**
1. Connect to your Hostinger server via SSH
2. Create `.env` file in project root:
   ```bash
   nano /home/yourusername/bhrikutimandap/.env
   ```
3. Add these settings:
   ```
   EMAIL_HOST=smtp.hostinger.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=admin@bhrikutimandap.com
   EMAIL_HOST_PASSWORD=Bhrikutimandap@2026$$$$
   DEFAULT_FROM_EMAIL=admin@bhrikutimandap.com
   CONTACT_EMAIL=admin@bhrikutimandap.com
   DJANGO_DEBUG=False
   ```
4. Save (Ctrl+O, Enter, Ctrl+X)

### Option 2: Ensure python-dotenv is Installed

Make sure `python-dotenv` is in your `requirements.txt`:

```bash
pip install python-dotenv
```

Add to requirements.txt:
```
python-dotenv>=0.19.0
```

### Option 3: Test Email Configuration Locally First

Before deploying, test the email configuration:

```bash
# Test Hostinger SMTP connection
python manage.py shell

# In Django shell:
from django.core.mail import send_mail
from django.conf import settings

try:
    send_mail(
        'Test Email from Bhrikutimandap',
        'This is a test email to verify SMTP settings.',
        'admin@bhrikutimandap.com',
        ['admin@bhrikutimandap.com'],
        fail_silently=False,
    )
    print("✓ Email sent successfully!")
except Exception as e:
    print(f"✗ Email failed: {e}")
```

## Hostinger SMTP Settings (Verified)

- **SMTP Server:** smtp.hostinger.com
- **SMTP Port:** 587
- **Security:** TLS (not SSL)
- **Username:** admin@bhrikutimandap.com
- **Password:** Bhrikutimandap@2026$$$$
- **From Email:** admin@bhrikutimandap.com

## Troubleshooting

### Error: "Client host rejected: Access denied"
- **Cause:** SMTP credentials are incorrect or IP is blacklisted
- **Solution:** 
  1. Verify credentials are exact (case-sensitive)
  2. Check Hostinger spam/blacklist settings
  3. Contact Hostinger support to whitelist server IP

### Error: "Connection refused"
- **Cause:** Port or host incorrect
- **Solution:** 
  1. Verify EMAIL_HOST = smtp.hostinger.com
  2. Verify EMAIL_PORT = 587
  3. Ensure EMAIL_USE_TLS = True

### Error: "Authentication failed"
- **Cause:** Wrong email or password
- **Solution:**
  1. Double-check Email_HOST_USER (should be admin@bhrikutimandap.com)
  2. Verify password exactly: Bhrikutimandap@2026$$$$
  3. Check if account is active in Hostinger

## Django Configuration in Settings.py

The system uses two email backends:

```python
if 'test' in sys.argv:
    EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'  # Testing
elif DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Development
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Production
```

**Important:** In production, `DEBUG` must be `False` for SMTP to be used.

## How Email is Sent

1. **Contact Form** → `contact_view()` in views.py
2. **Calls** → `_send_email()` helper function
3. **In Production** → Reads from environment variables
4. **Connects to** → Hostinger SMTP server (smtp.hostinger.com:587)
5. **Sends to** → admin@bhrikutimandap.com (from CONTACT_EMAIL)

## Deployment Checklist

- [ ] `requirements.txt` includes `python-dotenv>=0.19.0`
- [ ] `.env` file is in project root on production server
- [ ] OR environment variables are set in Hostinger control panel
- [ ] `DJANGO_DEBUG=False` is set in production
- [ ] Email credentials are exact (no typos)
- [ ] SMTP port is 587 (not 25, 465, etc.)
- [ ] TLS is enabled (EMAIL_USE_TLS=True)
- [ ] Test email sending before going live

## Contact Email Configuration

If you need emails to go to a different address, update in two places:

1. **In Django Admin:**
   - Go to `/admin/store/sitesettings/1/`
   - Update "Contact Email" field
   - OR update "Default From Email"

2. **Or in environment:**
   ```
   CONTACT_EMAIL=admin@bhrikutimandap.com
   DEFAULT_FROM_EMAIL=admin@bhrikutimandap.com
   ```

## Next Steps

1. Deploy the `.env` file to your Hostinger server with the updated credentials
2. Test the contact form to verify emails are sending
3. Check Hostinger email logs if issues persist
4. Monitor production logs for email errors

---

**Status:** ✅ Production email configuration documented
**Last Updated:** Jan 19, 2026
