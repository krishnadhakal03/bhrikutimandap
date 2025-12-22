# 🚀 Quick Start: Deploy to Hostinger in 30 Minutes

This is a condensed version of the complete deployment guide. For detailed instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## 📋 What You'll Need

- Hostinger Premium/Business hosting or VPS account
- Domain name
- 30 minutes of your time

---

## ⚡ Quick Deployment Steps

### 1. Prepare Locally (5 minutes)

```bash
# Clone the repository
git clone https://github.com/krishnadhakal03/bhrikutimandap.git
cd bhrikutimandap

# Copy environment template
cp .env.example .env

# Generate a secret key
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Edit .env with your details
nano .env
```

Update `.env` with:
- Your generated secret key
- Your domain name
- Database credentials (you'll create these in step 2)

### 2. Set Up Database on Hostinger (3 minutes)

1. Log in to Hostinger hPanel
2. Go to **Databases** → **MySQL Databases**
3. Click **Create Database**
4. Save these credentials and add them to your `.env` file

### 3. Upload Files to Hostinger (5 minutes)

**Option A: SSH + Git (Recommended)**
```bash
ssh username@yourdomain.com
cd public_html
git clone https://github.com/krishnadhakal03/bhrikutimandap.git
cd bhrikutimandap
```

**Option B: FTP/SFTP**
- Upload all files to `public_html/bhrikutimandap/`

### 4. Update Configuration Files (3 minutes)

Edit `passenger_wsgi.py` and `.htaccess` - replace `username` with your Hostinger username:

```bash
# In passenger_wsgi.py and .htaccess, change:
# /home/username/public_html/...
# to your actual username
```

### 5. Set Up Python Environment (5 minutes)

```bash
cd ~/public_html/bhrikutimandap

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 6. Initialize Django (5 minutes)

```bash
# Make sure you're in the project directory with venv activated
source venv/bin/activate

# Run migrations
python manage.py migrate --settings=market.production_settings

# Create admin user
python manage.py createsuperuser --settings=market.production_settings

# Collect static files
python manage.py collectstatic --noinput --settings=market.production_settings

# (Optional) Load sample data
python manage.py seed --settings=market.production_settings
```

### 7. Set Permissions & Launch (2 minutes)

```bash
# Set correct permissions
chmod -R 755 ~/public_html/bhrikutimandap
chmod -R 777 ~/public_html/bhrikutimandap/media
chmod 600 ~/public_html/bhrikutimandap/.env

# Create restart directory and restart
mkdir -p tmp
touch tmp/restart.txt
```

### 8. Test Your Site (2 minutes)

Visit these URLs and verify everything works:

- ✅ Homepage: `https://yourdomain.com`
- ✅ Admin Panel: `https://yourdomain.com/admin/`
- ✅ Agent Dashboard: `https://yourdomain.com/agent/dashboard/`

---

## 🎯 Essential Files Checklist

Make sure these files exist in your project:

- ✅ `passenger_wsgi.py` - Entry point for Passenger
- ✅ `.htaccess` - Web server configuration
- ✅ `.env` - Environment variables (not in Git)
- ✅ `market/production_settings.py` - Production settings
- ✅ `requirements.txt` - Python dependencies

---

## 🔧 Common Issues & Quick Fixes

**500 Internal Server Error**
```bash
# Check logs and restart
tail -f logs/django_errors.log
touch tmp/restart.txt
```

**Static files not loading**
```bash
python manage.py collectstatic --noinput --settings=market.production_settings
```

**Database connection error**
- Verify credentials in `.env`
- Test: `mysql -u DB_USER -p DB_NAME`

**Application not restarting**
```bash
touch tmp/restart.txt
# Wait 30 seconds for Passenger to restart
```

---

## 📚 Next Steps

After successful deployment:

1. **Configure SSL/HTTPS** in Hostinger hPanel
2. **Set up regular backups** (see [DEPLOYMENT.md](DEPLOYMENT.md))
3. **Configure email** for password resets (optional)
4. **Add monitoring** with Sentry or similar (optional)
5. **Review security** checklist in [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 📖 Full Documentation

For complete instructions, troubleshooting, and VPS deployment:
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Step-by-step checklist

---

## 🆘 Need Help?

1. Check the detailed [DEPLOYMENT.md](DEPLOYMENT.md)
2. Review [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
3. Search [Hostinger support](https://support.hostinger.com/)
4. Create an issue on [GitHub](https://github.com/krishnadhakal03/bhrikutimandap/issues)

---

**Quick Start Guide Version:** 1.0  
**Last Updated:** December 22, 2024  
**Estimated Time:** 30 minutes
