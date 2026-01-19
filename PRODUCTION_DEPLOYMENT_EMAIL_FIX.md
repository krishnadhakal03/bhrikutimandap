# Email Fix - Production Deployment Steps

## What Was Fixed

1. ✅ Updated `.env` file with actual Hostinger credentials
2. ✅ Improved error handling in contact form (better error messages)
3. ✅ Added debugging information to logs
4. ✅ Created comprehensive production email setup guide

## Required Actions on Hostinger Production Server

### Step 1: Deploy Updated Files
Upload these files to your production server:
- `.env` (with actual credentials)
- `store/views.py` (improved error handling)
- `PRODUCTION_EMAIL_SETUP.md` (reference guide)

### Step 2: Ensure Environment Variables are Set

**Best Method - SSH Access:**
```bash
# SSH into Hostinger server
ssh username@yourdomain.com

# Navigate to project
cd /home/yourusername/bhrikutimandap/

# Create/update .env file
nano .env
```

**Paste these settings:**
```
DJANGO_SECRET_KEY=<your-secret-key>
DJANGO_DEBUG=False
ALLOWED_HOSTS=bhrikutimandap.com,www.bhrikutimandap.com

# Email Configuration
EMAIL_HOST=smtp.hostinger.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=admin@bhrikutimandap.com
EMAIL_HOST_PASSWORD=Bhrikutimandap@2026$$$$
DEFAULT_FROM_EMAIL=admin@bhrikutimandap.com
CONTACT_EMAIL=admin@bhrikutimandap.com

# Database (if using PostgreSQL)
DATABASE_ENGINE=postgresql
DATABASE_NAME=<your-db-name>
DATABASE_USER=<your-db-user>
DATABASE_PASSWORD=<your-db-password>
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

**Save:** `Ctrl+O`, `Enter`, `Ctrl+X`

### Step 3: Restart Application
```bash
# If using Gunicorn/Supervisor
sudo systemctl restart bhrikutimandap
# OR
sudo supervisorctl restart bhrikutimandap

# If using Docker Compose
docker-compose restart web
```

### Step 4: Test Email Configuration
1. Go to `https://bhrikutimandap.com/contact/`
2. Fill out the contact form
3. Submit
4. You should receive email at admin@bhrikutimandap.com

**Check server logs for errors:**
```bash
tail -f /path/to/logs/django.log
```

## Troubleshooting

### Email Still Not Sending?

**Check Django settings are loaded:**
```bash
python manage.py shell
>>> from django.conf import settings
>>> print(settings.EMAIL_HOST)
>>> print(settings.EMAIL_HOST_USER)
>>> print(settings.DEBUG)
```

Should show:
```
smtp.hostinger.com
admin@bhrikutimandap.com
False
```

**Test SMTP connection directly:**
```bash
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail(
...     'Test Subject',
...     'Test message body',
...     'admin@bhrikutimandap.com',
...     ['admin@bhrikutimandap.com'],
...     fail_silently=False
... )
```

**Check Hostinger email logs:**
- Go to Hostinger Admin Panel
- Mail Management
- Review bounce/error logs

### Common Issues

| Error | Solution |
|-------|----------|
| "Connection refused" | Check EMAIL_HOST (smtp.hostinger.com) and EMAIL_PORT (587) |
| "Authentication failed" | Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are exact |
| "Client host rejected" | Contact Hostinger to whitelist your server IP |
| "Timeout" | Check if port 587 is open (firewall/ISP blocking) |

## Production Email Workflow

```
User fills Contact Form
        ↓
contact_view() in views.py
        ↓
_send_email() function
        ↓
Reads from environment (.env)
        ↓
Connects to SMTP server (smtp.hostinger.com:587)
        ↓
Sends email via TLS encryption
        ↓
Email arrives at admin@bhrikutimandap.com
        ↓
User sees "Thanks for contacting us" message
```

## Key Settings Reference

| Setting | Value | Purpose |
|---------|-------|---------|
| EMAIL_HOST | smtp.hostinger.com | Hostinger SMTP server |
| EMAIL_PORT | 587 | Standard SMTP TLS port |
| EMAIL_USE_TLS | True | Encrypt connection |
| EMAIL_HOST_USER | admin@bhrikutimandap.com | Login credentials |
| EMAIL_HOST_PASSWORD | Bhrikutimandap@2026$$$$ | Password (keep secret!) |
| DEFAULT_FROM_EMAIL | admin@bhrikutimandap.com | Sender address |
| CONTACT_EMAIL | admin@bhrikutimandap.com | Where contact form emails go |
| DJANGO_DEBUG | False | MUST be False in production |

## Security Notes

⚠️ **Important:**
- Never commit `.env` file with passwords to GitHub
- Keep `.env` file permissions restricted (600)
- Use unique, strong passwords
- Consider using Hostinger's email masking if available
- Monitor email logs regularly

## Support

If email issues persist:
1. Contact Hostinger support with these details:
   - Email: admin@bhrikutimandap.com
   - SMTP Server: smtp.hostinger.com
   - Port: 587
   - TLS: Enabled

2. Check Django logs: `tail -f /var/log/django/error.log`

3. Check mail logs: `tail -f /var/log/mail.log`

---

**Status:** ✅ Production email configuration ready
**Date:** Jan 19, 2026
