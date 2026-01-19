# Dynamic Email Configuration - Admin Control

## Overview

You can now manage email (SMTP) settings directly from the Django admin panel without touching code or `.env` files. This is perfect for production where you need to change credentials at runtime.

## Features

✅ **Manage SMTP Settings in Admin Panel** - Change email host, port, username, password  
✅ **Runtime Configuration** - No server restart needed (in most cases)  
✅ **Fallback to .env** - If database settings are empty, uses `.env` values  
✅ **Works with Development & Production** - Console output in DEBUG mode, SMTP in production  
✅ **Secure Password Storage** - Passwords stored in database  

## Step-by-Step Setup

### 1. Run Migration

Apply the new database migration to add email fields to SiteSettings:

```bash
python manage.py migrate
```

This creates 6 new fields in the `store_sitesettings` table:
- `email_host` - SMTP server (default: smtp.hostinger.com)
- `email_port` - SMTP port (default: 587)
- `email_use_tls` - Use TLS (default: True)
- `email_host_user` - SMTP username (default: admin@bhrikutimandap.com)
- `email_host_password` - SMTP password
- `default_from_email` - Sender email (default: admin@bhrikutimandap.com)

### 2. Configure in Admin Panel

1. Login to Django Admin: `/admin/`
2. Go to **Store Settings** → **Site Settings**
3. Scroll down to **"Email Configuration (SMTP)"** section
4. Fill in your Hostinger credentials:
   - **Email Host**: `smtp.hostinger.com`
   - **Email Port**: `587`
   - **Email Use TLS**: ✓ (checked)
   - **Email Host User**: `admin@bhrikutimandap.com`
   - **Email Host Password**: Your Hostinger password
   - **Default From Email**: `admin@bhrikutimandap.com`
5. Click **Save**

### 3. Test Email Sending

**In Development (DEBUG=True):**
- Emails print to console
- No actual SMTP needed
- Password can be left empty

**In Production (DEBUG=False):**
- Set password in admin
- Emails sent via SMTP
- Test with admin panel first

## How It Works

### Local Development Flow

```
Contact Form / Registration
    ↓
_send_email() function
    ↓
Check if DEBUG mode
    ↓
If DEBUG=True → Console backend (print to terminal)
If DEBUG=False → _get_email_connection()
    ↓
_get_email_connection()
    ↓
Try to get SiteSettings from database
    ↓
If available → Use SiteSettings values
If not available → Use .env values
    ↓
Send via SMTP
```

### Functions Added

**1. `_get_email_connection()`**
- Gets SMTP connection with settings from SiteSettings
- Falls back to environment variables if SiteSettings not available
- Located in `store/views.py`

**2. `_get_from_email()`**
- Gets DEFAULT_FROM_EMAIL from SiteSettings
- Falls back to `settings.DEFAULT_FROM_EMAIL`
- Located in `store/views.py`

**3. `_send_email()`**
- Wrapper around Django's `send_mail()`
- Uses dynamic SMTP connection
- Works in both DEBUG and production modes
- Located in `store/views.py`

## Where Email is Used

### 1. Registration Email
**File**: `store/views.py` → `register_view()`
- Sends activation link to new users
- Uses `_get_from_email()` to get sender
- Uses `_send_email()` to send

### 2. Contact Form Email
**File**: `store/views.py` → `contact_view()`
- Sends contact message to `contact_email` from SiteSettings
- Falls back to `settings.CONTACT_EMAIL` if not set
- Uses `_send_email()` to send

## Changing Email at Runtime

### Scenario 1: Change SMTP Password
1. Go to Admin → Site Settings
2. Update **Email Host Password** field
3. Click **Save**
4. Next email will use new password

### Scenario 2: Change SMTP Server
1. Go to Admin → Site Settings
2. Update **Email Host** to new server
3. Update **Email Port** if needed
4. Click **Save**
5. Restart Django (some servers cache connections)

### Scenario 3: Change Sender Email
1. Go to Admin → Site Settings
2. Update **Default From Email**
3. Click **Save**
4. Next email uses new sender

## Fallback Behavior

If there's an error loading SiteSettings:
1. Uses values from `.env` file
2. Logs debug message
3. Email still sends using environment defaults

This means **you're never stuck** - if database has issues, the system falls back to `.env` configuration.

## Database vs Environment Variables

| Setting | Priority | Local Dev | Production |
|---------|----------|-----------|------------|
| Email Host | SiteSettings > .env | smtp.hostinger.com | Read from admin |
| Email Port | SiteSettings > .env | 587 | Read from admin |
| Email TLS | SiteSettings > .env | True | Read from admin |
| Email User | SiteSettings > .env | admin@bhrikutimandap.com | Read from admin |
| Email Password | SiteSettings > .env | (leave empty in dev) | Read from admin |
| From Email | SiteSettings > .env | admin@bhrikutimandap.com | Read from admin |

## Files Modified/Created

### Created
- `market/email_config.py` - Email configuration helper (optional, for reference)
- `market/dynamic_email_backend.py` - Custom SMTP backend (optional, alternative approach)
- `store/migrations/0012_sitesettings_email_config.py` - Database migration

### Modified
- `store/models.py` - Added 6 email fields to SiteSettings
- `store/admin.py` - Added email fieldset to SiteSettingsAdmin
- `store/views.py` - Added dynamic email functions, updated contact_view() and register_view()

## Best Practices

1. **In Development**: Leave password empty, DEBUG=True, see emails in console
2. **In Production**: Set DEBUG=False, add password in admin, test before going live
3. **Sensitive Data**: Consider using Docker secrets or environment variables for password instead of storing in database
4. **Backup**: Keep `.env` file as backup configuration
5. **Testing**: Always test email sending after changing settings

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Connection refused" | Check Email Host and Email Port are correct |
| "Authentication failed" | Verify Email Host User and Email Host Password |
| Emails not sending | Check DEBUG=True (console mode) or verify SMTP credentials |
| Emails in spam | May need to whitelist sender domain in Hostinger |
| Settings not applying | Restart Django server or clear connection cache |

## Next Steps

1. Run migration: `python manage.py migrate`
2. Go to Admin → Site Settings
3. Fill in Hostinger email credentials
4. Test by creating a registration or submitting contact form
5. Watch terminal or admin logs for email output

