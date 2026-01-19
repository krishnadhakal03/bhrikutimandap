# Quick Reference - Dynamic Email Configuration

## 🚀 Get Started in 3 Steps

### Step 1: Apply Migration
```bash
python manage.py migrate
```

### Step 2: Go to Admin Panel
```
http://localhost:8000/admin/store/sitesettings/1/change/
```

### Step 3: Scroll to "Email Configuration (SMTP)" and Fill In:
```
Email Host:           smtp.hostinger.com
Email Port:           587
Email Use TLS:        ✓ (checked)
Email Host User:      admin@bhrikutimandap.com
Email Host Password:  your-hostinger-password
Default From Email:   admin@bhrikutimandap.com
```

**Click Save** ✓

---

## 📧 How Emails Are Sent

### 1. Registration Email
- When: User creates account
- Goes to: User's email address
- Subject: "Activate your account"
- Contains: Activation link

### 2. Contact Form Email
- When: User submits contact form
- Goes to: `contact_email` from SiteSettings
- Subject: "Contact Form: {subject}"
- Contains: Sender info + message

---

## 🔄 Priority Order (Highest → Lowest)

1. **Admin Panel** (SiteSettings in database) ← **Use this for production**
2. `.env` file (environment variables) ← **Use this for development**
3. Hardcoded defaults ← **Fallback only**

---

## 🛠️ Change Settings at Runtime

**Before**: Edit `.env` + restart server ❌  
**Now**: Update Admin Panel + done ✅

### To Change Email Credentials:
1. Admin Panel → Site Settings
2. Update any field
3. Click Save
4. Next email uses new settings

### To Test New Settings:
1. Register a test account
2. Check console/logs for email output
3. Verify it uses new credentials

---

## 📝 What Each Field Does

| Field | Example | Purpose |
|-------|---------|---------|
| Email Host | smtp.hostinger.com | SMTP server address |
| Email Port | 587 | SMTP connection port |
| Email Use TLS | ✓ | Enable encryption |
| Email Host User | admin@bhrikutimandap.com | SMTP login username |
| Email Host Password | your-password | SMTP login password |
| Default From Email | admin@bhrikutimandap.com | Sender's email address |

---

## 🧪 Testing

### Development Mode (DEBUG=True)
```bash
# Emails print to terminal - no SMTP needed
# Run Django:
python manage.py runserver

# Create test account or submit form
# Check terminal for email output ↓

# ------------------- EMAIL MESSAGE -------------------
# From: admin@bhrikutimandap.com
# To: ['user@example.com']
# Subject: Activate your account
# -------------------------------------------------------
```

### Production Mode (DEBUG=False)
```bash
# Emails sent via SMTP - requires valid credentials
# Set in admin panel + restart server
# Test with real email addresses
# Monitor logs for errors
```

---

## ⚠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| "Connection refused" | Check Email Host & Port are correct |
| "Authentication failed" | Verify password is correct |
| Emails not sent | Check DEBUG mode or SMTP credentials |
| Changes not applied | Restart Django server |
| Can't login to admin | Use `/admin/` URL, check superuser created |

---

## 📂 Files That Changed

| File | What Changed |
|------|--------------|
| `store/models.py` | Added 6 email fields to SiteSettings |
| `store/admin.py` | Added Email fieldset to admin |
| `store/views.py` | Added 3 helper functions for dynamic emails |
| `store/migrations/0012_...` | NEW - Database schema update |

---

## 🔐 Security Notes

- Passwords stored in database (consider adding encryption layer later)
- Always use `.env` for local secrets
- For production, consider using Django secrets management
- Keep `.env` file as backup configuration

---

## 📚 More Information

- Full guide: `DYNAMIC_EMAIL_CONFIG.md`
- Setup summary: `DYNAMIC_EMAIL_SUMMARY.md`
- Original setup: `EMAIL_SETUP.md`

---

## ✅ What's Working Now

✓ Account registration emails  
✓ Contact form email delivery  
✓ Admin panel configuration  
✓ Runtime credential changes  
✓ Fallback to .env if needed  
✓ Console mode for development  
✓ SMTP mode for production  

---

**Need help?** Check the detailed documentation in `DYNAMIC_EMAIL_CONFIG.md`

