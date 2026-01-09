# Django Project Deployment Guide - Hostinger VPS

This guide will help you deploy your Bhrikutimandap Django project to Hostinger VPS with your GoDaddy domain.

## Prerequisites
- Hostinger VPS access (SSH credentials)
- GoDaddy domain registered
- Your project on GitHub: https://github.com/krishnadhakal03/bhrikutimandap
- Basic Linux/terminal knowledge

---

## Phase 1: Prepare Your Project (Do This First on Local Machine)

### 1.1 Update Settings for Production

**Step 1:** Update [market/settings.py](market/settings.py) for production:

```python
# In market/settings.py, modify these settings:

DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

# Replace ALLOWED_HOSTS with your actual domain
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com', 'your-vps-ip']

# Add security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### 1.2 Create .env File Template

Create a `.env.example` file in your project root (do NOT commit the actual .env):

```
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_NAME=bhrikuti_db
DATABASE_USER=bhrikuti_user
DATABASE_PASSWORD=strong-password-here
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

### 1.3 Update requirements.txt

Ensure your [requirements.txt](requirements.txt) includes production packages:

```
Django>=4.2,<5.0
Pillow>=10.0.0
django-widget-tweaks>=1.4.12
gunicorn>=21.0.0
python-dotenv>=1.0.0
psycopg2-binary>=2.9.0
whitenoise>=6.4.0
```

### 1.4 Commit and Push Changes

```bash
git add .
git commit -m "Prepare for production deployment"
git push origin main
```

---

## Phase 2: Server Setup on Hostinger VPS

### 2.1 Connect to Your VPS

```bash
ssh root@your-vps-ip-address
# Or if you have a username:
ssh username@your-vps-ip-address
```

### 2.2 Update System Packages

```bash
apt update
apt upgrade -y
```

### 2.3 Install Required Software

```bash
# Python and pip
apt install -y python3 python3-pip python3-venv python3-dev

# Database (PostgreSQL)
apt install -y postgresql postgresql-contrib

# Web server and process manager
apt install -y nginx

# Build tools
apt install -y build-essential libssl-dev libffi-dev

# Git
apt install -y git

# Certbot for SSL
apt install -y certbot python3-certbot-nginx

# Supervisor (process manager)
apt install -y supervisor
```

### 2.4 Create Application User

```bash
useradd -m -s /bin/bash bhrikuti
usermod -aG sudo bhrikuti
```

---

## Phase 3: Database Setup

### 3.1 Create PostgreSQL Database

```bash
sudo -u postgres psql
```

In PostgreSQL prompt:

```sql
CREATE DATABASE bhrikuti_db;
CREATE USER bhrikuti_user WITH PASSWORD 'your-strong-password';
ALTER ROLE bhrikuti_user SET client_encoding TO 'utf8';
ALTER ROLE bhrikuti_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE bhrikuti_user SET default_transaction_deferrable TO on;
ALTER ROLE bhrikuti_user SET default_transaction_level TO 'read committed';
GRANT ALL PRIVILEGES ON DATABASE bhrikuti_db TO bhrikuti_user;
\q
```

---

## Phase 4: Clone and Setup Project

### 4.1 Clone Repository

```bash
cd /home/bhrikuti
sudo -u bhrikuti git clone https://github.com/krishnadhakal03/bhrikutimandap.git
cd bhrikutimandap
```

### 4.2 Create Virtual Environment

```bash
cd /home/bhrikuti/bhrikutimandap
python3 -m venv venv
source venv/bin/activate
```

### 4.3 Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.4 Create .env File

```bash
sudo nano .env
```

Add the following (replace values with actual ones):

```
DJANGO_SECRET_KEY=your-very-secret-key-change-this
DJANGO_DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-vps-ip
DATABASE_NAME=bhrikuti_db
DATABASE_USER=bhrikuti_user
DATABASE_PASSWORD=your-strong-password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

Press `Ctrl+X`, then `Y`, then `Enter` to save.

### 4.5 Run Migrations

```bash
source venv/bin/activate
python manage.py migrate
```

### 4.6 Create Superuser

```bash
python manage.py createsuperuser
```

### 4.7 Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 4.8 Fix Permissions

```bash
sudo chown -R bhrikuti:bhrikuti /home/bhrikuti/bhrikutimandap
chmod -R 755 /home/bhrikuti/bhrikutimandap
```

---

## Phase 5: Configure Gunicorn

### 5.1 Create Gunicorn Service File

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Add the following:

```ini
[Unit]
Description=Gunicorn application server for Bhrikutimandap
After=network.target

[Service]
Type=notify
User=bhrikuti
Group=www-data
WorkingDirectory=/home/bhrikuti/bhrikutimandap
ExecStart=/home/bhrikuti/bhrikutimandap/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/home/bhrikuti/bhrikutimandap/gunicorn.sock \
    market.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
KillSignal=SIGTERM
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

### 5.2 Enable and Start Gunicorn

```bash
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn
```

---

## Phase 6: Configure Nginx

### 6.1 Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/bhrikutimandap
```

Add the following:

```nginx
upstream gunicorn {
    server unix:/home/bhrikuti/bhrikutimandap/gunicorn.sock;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    client_max_body_size 20M;

    location / {
        proxy_pass http://gunicorn;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/bhrikuti/bhrikutimandap/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /home/bhrikuti/bhrikutimandap/media/;
        expires 7d;
    }
}
```

### 6.2 Enable Nginx Site

```bash
sudo ln -s /etc/nginx/sites-available/bhrikutimandap /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Phase 7: Setup SSL Certificate (HTTPS)

### 7.1 Get SSL Certificate with Certbot

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Follow the prompts and choose to redirect HTTP to HTTPS.

### 7.2 Auto-renewal Setup

Certbot should automatically setup renewal. Verify:

```bash
sudo certbot renew --dry-run
```

---

## Phase 8: Configure DNS on GoDaddy

### 8.1 Point Domain to VPS

1. Log in to GoDaddy
2. Go to **DNS Management** for your domain
3. Update **A Record**:
   - Host: `@` (for root domain)
   - Type: A
   - Points to: `your-vps-ip-address`
   - TTL: 600 (or default)

4. Add **CNAME Record** for www:
   - Host: `www`
   - Type: CNAME
   - Points to: `yourdomain.com`
   - TTL: 600

5. Wait 24-48 hours for DNS propagation (check with: `nslookup yourdomain.com`)

---

## Phase 9: Post-Deployment Checks

### 9.1 Verify Services

```bash
# Check Gunicorn
sudo systemctl status gunicorn

# Check Nginx
sudo systemctl status nginx

# Check PostgreSQL
sudo systemctl status postgresql

# View Gunicorn logs
sudo journalctl -u gunicorn -n 20
```

### 9.2 Test Application

```bash
# Access Django shell
cd /home/bhrikuti/bhrikutimandap
source venv/bin/activate
python manage.py shell
```

### 9.3 Monitor Disk Space

```bash
df -h
```

---

## Phase 10: Maintenance & Monitoring

### 10.1 Regular Backups

```bash
# Backup database weekly
sudo -u postgres pg_dump bhrikuti_db > /home/bhrikuti/backups/bhrikuti_db_$(date +%Y%m%d).sql
```

### 10.2 Check Log Files

```bash
# Django logs
sudo tail -f /var/log/nginx/error.log

# Application logs
sudo journalctl -u gunicorn -f
```

### 10.3 Update Project

When you push updates to GitHub:

```bash
cd /home/bhrikuti/bhrikutimandap
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

---

## Troubleshooting

### Issue: Domain not resolving
- **Solution**: Wait for DNS propagation (24-48 hours), check DNS records in GoDaddy

### Issue: SSL certificate errors
```bash
sudo certbot renew
sudo systemctl restart nginx
```

### Issue: Gunicorn socket permission error
```bash
sudo chown -R bhrikuti:www-data /home/bhrikuti/bhrikutimandap
```

### Issue: Static files not loading
```bash
python manage.py collectstatic --noinput --clear
sudo systemctl restart nginx
```

### Issue: Database connection error
```bash
# Check PostgreSQL is running
sudo systemctl restart postgresql

# Verify .env variables match database
```

### View Application Errors
```bash
sudo journalctl -u gunicorn -n 50 --no-pager
```

---

## Quick Reference Commands

```bash
# SSH into VPS
ssh root@your-vps-ip

# Activate virtual environment
cd /home/bhrikuti/bhrikutimandap && source venv/bin/activate

# Restart application
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# Pull latest code
cd /home/bhrikuti/bhrikutimandap && git pull origin main

# Migrate database
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser

# View logs
sudo journalctl -u gunicorn -f
```

---

## Security Checklist

- [ ] Change PostgreSQL password
- [ ] Set strong SECRET_KEY in .env
- [ ] Update ALLOWED_HOSTS with actual domain
- [ ] Enable SSL/TLS (Certbot)
- [ ] Configure firewall
- [ ] Regular backups setup
- [ ] Monitor disk space
- [ ] Keep system updated

---

## Support Resources

- Django Documentation: https://docs.djangoproject.com/
- Gunicorn: https://gunicorn.org/
- Nginx: https://nginx.org/
- Let's Encrypt: https://letsencrypt.org/
- PostgreSQL: https://www.postgresql.org/

---

**Last Updated**: January 2026
