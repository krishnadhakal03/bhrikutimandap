# 🚀 Deploying Bhrikutimandap to Hostinger

This guide provides step-by-step instructions for deploying the Bhrikutimandap e-commerce platform to Hostinger hosting.

## 📋 Table of Contents
- [Prerequisites](#prerequisites)
- [Hostinger Account Setup](#hostinger-account-setup)
- [Deployment Methods](#deployment-methods)
  - [Method 1: Python App Deployment (Recommended)](#method-1-python-app-deployment-recommended)
  - [Method 2: VPS Deployment](#method-2-vps-deployment)
- [Database Configuration](#database-configuration)
- [Static Files & Media](#static-files--media)
- [Environment Variables](#environment-variables)
- [Post-Deployment Steps](#post-deployment-steps)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

---

## Prerequisites

Before deploying to Hostinger, ensure you have:

1. **Hostinger Account** 
   - Premium or Business shared hosting plan (for Python support)
   - OR VPS hosting plan (recommended for better performance)

2. **Domain Name**
   - Registered and pointed to Hostinger nameservers

3. **Local Project Setup**
   - Working Django application
   - All dependencies listed in `requirements.txt`
   - Database populated with initial data

4. **Required Tools**
   - Git installed locally
   - SSH client (for VPS deployment)
   - FTP/SFTP client (FileZilla, WinSCP, or similar)

---

## Hostinger Account Setup

### 1. Choose Your Hosting Plan

**Option A: Shared Hosting (Python App)**
- Premium or Business shared hosting with Python support
- Suitable for small to medium traffic
- Limited customization
- Cost-effective

**Option B: VPS Hosting (Recommended)**
- Full server control
- Better performance and scalability
- Can handle higher traffic
- Requires more technical knowledge

### 2. Access Your Control Panel
- Log in to Hostinger at https://www.hostinger.com
- Navigate to **hPanel** (Hostinger's control panel)

---

## Deployment Methods

## Method 1: Python App Deployment (Recommended)

This method is suitable for Hostinger's shared hosting plans with Python support.

### Step 1: Prepare Your Project

1. **Update requirements.txt for production:**
```bash
# On your local machine
pip freeze > requirements.txt
```

Ensure your `requirements.txt` includes:
```
django>=4.2
mysqlclient
Pillow
django-widget-tweaks
gunicorn
whitenoise
python-dotenv
```

2. **Create production settings file:**

Create `market/production_settings.py`:
```python
from .settings import *
import os

# Security settings
DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = [os.environ.get('DOMAIN_NAME'), 'www.' + os.environ.get('DOMAIN_NAME')]

# Database - Use MySQL for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# WhiteNoise middleware for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
```

### Step 2: Set Up Database on Hostinger

1. In **hPanel**, go to **Databases** → **MySQL Databases**
2. Click **Create Database**
3. Note down:
   - Database name
   - Database user
   - Database password
   - Database host (usually `localhost`)

### Step 3: Upload Your Project

**Option A: Using Git (Recommended)**

1. In hPanel, open **SSH Access** and enable it
2. Connect via SSH:
```bash
ssh username@yourdomain.com
```

3. Clone your repository:
```bash
cd public_html
git clone https://github.com/krishnadhakal03/bhrikutimandap.git
cd bhrikutimandap
```

**Option B: Using FTP/SFTP**

1. Connect to your hosting via FTP/SFTP
2. Upload all project files to `public_html/bhrikutimandap/`

### Step 4: Set Up Python Environment

1. SSH into your server
2. Create virtual environment:
```bash
cd ~/public_html/bhrikutimandap
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Step 5: Create Passenger WSGI File

Create `passenger_wsgi.py` in your project root:

```python
import sys
import os

# Add project directory to the sys.path
INTERP = os.path.expanduser("~/public_html/bhrikutimandap/venv/bin/python")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Add project path
sys.path.insert(0, os.path.expanduser('~/public_html/bhrikutimandap'))

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'market.production_settings'

# Import Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Step 6: Configure .htaccess

Create `.htaccess` in your project root:

```apache
# Force HTTPS
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Python application
PassengerEnabled On
PassengerAppRoot /home/username/public_html/bhrikutimandap
PassengerBaseURI /
PassengerPython /home/username/public_html/bhrikutimandap/venv/bin/python

# Static files
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_URI} !^/static/
RewriteCond %{REQUEST_URI} !^/media/
RewriteRule ^(.*)$ passenger_wsgi.py [QSA,L]
```

### Step 7: Set Environment Variables

Create `.env` file in project root:

```env
# Django settings
DJANGO_SECRET_KEY=your-super-secret-key-here-change-this
DJANGO_DEBUG=0
DOMAIN_NAME=yourdomain.com

# Database settings
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=3306

# Site settings
SITE_URL=https://yourdomain.com
```

**Important:** Generate a new secret key:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### Step 8: Run Migrations and Collect Static Files

```bash
cd ~/public_html/bhrikutimandap
source venv/bin/activate

# Load environment variables
export $(cat .env | xargs)

# Run migrations
python manage.py migrate --settings=market.production_settings

# Create superuser
python manage.py createsuperuser --settings=market.production_settings

# Collect static files
python manage.py collectstatic --noinput --settings=market.production_settings

# (Optional) Load sample data
python manage.py seed --settings=market.production_settings
```

### Step 9: Set File Permissions

```bash
chmod -R 755 ~/public_html/bhrikutimandap
chmod -R 777 ~/public_html/bhrikutimandap/media
find ~/public_html/bhrikutimandap -type f -name "*.py" -exec chmod 644 {} \;
chmod 600 .env
```

### Step 10: Restart Application

Create a `tmp` directory and touch a restart file:
```bash
mkdir -p tmp
touch tmp/restart.txt
```

---

## Method 2: VPS Deployment

For VPS hosting, you have more control and can use Gunicorn + Nginx.

### Prerequisites
- Hostinger VPS plan
- Ubuntu/Debian VPS
- Root or sudo access

### Step 1: Connect to VPS

```bash
ssh root@your_vps_ip
```

### Step 2: Update System

```bash
apt update && apt upgrade -y
```

### Step 3: Install Dependencies

```bash
# Install Python and tools
apt install -y python3 python3-pip python3-venv git

# Install MySQL
apt install -y mysql-server mysql-client libmysqlclient-dev

# Install Nginx
apt install -y nginx

# Install supervisor (for process management)
apt install -y supervisor
```

### Step 4: Set Up MySQL Database

```bash
mysql -u root -p
```

```sql
CREATE DATABASE bhrikutimandap CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'bhrikutiuser'@'localhost' IDENTIFIED BY 'strong_password_here';
GRANT ALL PRIVILEGES ON bhrikutimandap.* TO 'bhrikutiuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 5: Clone and Set Up Project

```bash
cd /var/www
git clone https://github.com/krishnadhakal03/bhrikutimandap.git
cd bhrikutimandap

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

### Step 6: Configure Environment

Create `.env`:
```bash
nano .env
```

Add:
```env
DJANGO_SECRET_KEY=your-generated-secret-key
DJANGO_DEBUG=0
DOMAIN_NAME=yourdomain.com
DB_NAME=bhrikutimandap
DB_USER=bhrikutiuser
DB_PASSWORD=strong_password_here
DB_HOST=localhost
DB_PORT=3306
SITE_URL=https://yourdomain.com
```

### Step 7: Update Production Settings

Ensure `market/production_settings.py` loads from `.env`:

```python
from .settings import *
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

DEBUG = False
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = [os.getenv('DOMAIN_NAME'), 'www.' + os.getenv('DOMAIN_NAME')]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
    }
}

# Static and media files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# WhiteNoise for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Step 8: Run Migrations

```bash
source venv/bin/activate
python manage.py migrate --settings=market.production_settings
python manage.py createsuperuser --settings=market.production_settings
python manage.py collectstatic --noinput --settings=market.production_settings
```

### Step 9: Configure Gunicorn

Create `/etc/supervisor/conf.d/bhrikutimandap.conf`:

```ini
[program:bhrikutimandap]
command=/var/www/bhrikutimandap/venv/bin/gunicorn --workers 3 --bind unix:/var/www/bhrikutimandap/bhrikutimandap.sock market.wsgi:application --env DJANGO_SETTINGS_MODULE=market.production_settings
directory=/var/www/bhrikutimandap
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/bhrikutimandap.log
environment=PATH="/var/www/bhrikutimandap/venv/bin"
```

### Step 10: Configure Nginx

Create `/etc/nginx/sites-available/bhrikutimandap`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/bhrikutimandap/staticfiles/;
    }

    location /media/ {
        alias /var/www/bhrikutimandap/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/bhrikutimandap/bhrikutimandap.sock;
    }
}
```

Enable the site:
```bash
ln -s /etc/nginx/sites-available/bhrikutimandap /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### Step 11: Start Services

```bash
supervisorctl reread
supervisorctl update
supervisorctl start bhrikutimandap
```

### Step 12: Set Up SSL with Let's Encrypt

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## Database Configuration

### MySQL Setup

1. **Create Database** (if not already done)
2. **Update settings** to use MySQL
3. **Install MySQL client:**
```bash
pip install mysqlclient
```

### PostgreSQL (Alternative)

If you prefer PostgreSQL:

1. Install PostgreSQL:
```bash
apt install postgresql postgresql-contrib libpq-dev
```

2. Create database:
```bash
sudo -u postgres psql
CREATE DATABASE bhrikutimandap;
CREATE USER bhrikutiuser WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE bhrikutimandap TO bhrikutiuser;
\q
```

3. Update requirements.txt:
```
psycopg2-binary
```

4. Update database settings:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bhrikutimandap',
        'USER': 'bhrikutiuser',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## Static Files & Media

### Collect Static Files

```bash
python manage.py collectstatic --noinput --settings=market.production_settings
```

### Media Files Permissions

```bash
chmod -R 755 media/
chown -R www-data:www-data media/
```

### Using WhiteNoise (Recommended)

WhiteNoise serves static files efficiently:

1. Install:
```bash
pip install whitenoise
```

2. Add to `MIDDLEWARE` in settings:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add here
    # ... other middleware
]
```

3. Configure:
```python
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

---

## Environment Variables

### Required Environment Variables

Create `.env` file with:

```env
# Django Core
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=0
DOMAIN_NAME=yourdomain.com

# Database
DB_NAME=bhrikutimandap
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306

# Site
SITE_URL=https://yourdomain.com

# Email (Optional)
EMAIL_HOST=smtp.hostinger.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@yourdomain.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### Load Environment Variables

Install python-dotenv:
```bash
pip install python-dotenv
```

In `production_settings.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Post-Deployment Steps

### 1. Create Superuser

```bash
python manage.py createsuperuser --settings=market.production_settings
```

### 2. Test Your Site

Visit:
- Homepage: `https://yourdomain.com`
- Admin: `https://yourdomain.com/admin/`
- Agent Dashboard: `https://yourdomain.com/agent/dashboard/`

### 3. Load Initial Data (Optional)

```bash
python manage.py seed --settings=market.production_settings
```

### 4. Set Up Regular Backups

**Database Backup Script:**

Create `/root/backup_db.sh`:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/root/backups"
mkdir -p $BACKUP_DIR
mysqldump -u bhrikutiuser -p'password' bhrikutimandap > $BACKUP_DIR/bhrikutimandap_$DATE.sql
# Keep only last 7 days
find $BACKUP_DIR -name "bhrikutimandap_*.sql" -mtime +7 -delete
```

Make executable and add to cron:
```bash
chmod +x /root/backup_db.sh
crontab -e
# Add: 0 2 * * * /root/backup_db.sh
```

### 5. Monitor Logs

**View Logs:**
```bash
# Application logs (VPS)
tail -f /var/log/bhrikutimandap.log

# Nginx logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

---

## Troubleshooting

### Issue: 500 Internal Server Error

**Solution:**
1. Check logs for errors
2. Ensure `DEBUG=False` in production
3. Check `ALLOWED_HOSTS` includes your domain
4. Verify database connection
5. Check file permissions

```bash
# Check logs
tail -f /var/log/bhrikutimandap.log

# Test Django settings
python manage.py check --settings=market.production_settings
```

### Issue: Static Files Not Loading

**Solution:**
1. Run `collectstatic`:
```bash
python manage.py collectstatic --noinput --settings=market.production_settings
```

2. Check STATIC_ROOT and STATIC_URL
3. Verify Nginx/Apache configuration
4. Clear browser cache

### Issue: Database Connection Failed

**Solution:**
1. Verify database credentials
2. Check database server is running:
```bash
systemctl status mysql
```

3. Test connection:
```bash
mysql -u bhrikutiuser -p bhrikutimandap
```

### Issue: Permission Denied on Media Uploads

**Solution:**
```bash
chmod -R 755 media/
chown -R www-data:www-data media/
```

### Issue: Application Not Restarting

**Shared Hosting:**
```bash
touch tmp/restart.txt
```

**VPS:**
```bash
supervisorctl restart bhrikutimandap
systemctl restart nginx
```

---

## Maintenance

### Update Application

```bash
cd /var/www/bhrikutimandap
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --settings=market.production_settings
python manage.py collectstatic --noinput --settings=market.production_settings
supervisorctl restart bhrikutimandap  # For VPS
# OR
touch tmp/restart.txt  # For shared hosting
```

### Monitor Performance

1. **Install monitoring tools:**
```bash
pip install django-debug-toolbar  # Development only
pip install sentry-sdk  # Production monitoring
```

2. **Set up application monitoring** with services like:
   - Sentry (error tracking)
   - New Relic (performance monitoring)
   - Google Analytics (user tracking)

### Security Checklist

- ✅ `DEBUG = False` in production
- ✅ Strong `SECRET_KEY`
- ✅ HTTPS enabled (SSL certificate)
- ✅ Secure cookies (`SESSION_COOKIE_SECURE = True`)
- ✅ Database credentials secured
- ✅ `.env` file protected (chmod 600)
- ✅ Regular security updates
- ✅ Firewall configured (for VPS)
- ✅ Regular backups scheduled

---

## Additional Resources

### Hostinger Documentation
- [Hostinger Help Center](https://support.hostinger.com/)
- [Python App Deployment](https://support.hostinger.com/en/articles/3628733-how-to-set-up-a-python-app)

### Django Documentation
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Django Production Settings](https://docs.djangoproject.com/en/stable/howto/deployment/)

### Support

For issues specific to this project:
- Create an issue on [GitHub](https://github.com/krishnadhakal03/bhrikutimandap/issues)
- Check project documentation: `CUSTOMER_JOURNEY.md`, `AGENT_JOURNEY.md`

---

## Quick Reference

### Common Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
python manage.py migrate --settings=market.production_settings

# Create superuser
python manage.py createsuperuser --settings=market.production_settings

# Collect static files
python manage.py collectstatic --noinput --settings=market.production_settings

# Restart application (Shared)
touch tmp/restart.txt

# Restart application (VPS)
supervisorctl restart bhrikutimandap
systemctl restart nginx

# View logs
tail -f /var/log/bhrikutimandap.log
```

---

**Deployment Guide Version:** 1.0  
**Last Updated:** December 22, 2024  
**Tested On:** Hostinger Shared Hosting & VPS

Good luck with your deployment! 🚀
