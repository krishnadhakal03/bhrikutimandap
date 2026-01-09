# Step-by-Step Production Deployment: Hostinger VPS + GoDaddy

**Status**: ✅ Production release committed to GitHub
**Release**: Production v1.0 - PostgreSQL + Security Settings

---

## STEP 1: Get Your Hostinger VPS Information

### What You Need:
1. **VPS IP Address** (e.g., 192.168.1.100)
2. **Root Password** or **SSH Username/Password**
3. **SSH Port** (usually 22)

### Where to Find It:
- Log in to **Hostinger Control Panel**
- Navigate to **Hosting** → **VPS**
- Find your VPS and click it
- Look for **IP Address** in the VPS details
- Click **Manage** → **Access** to get SSH credentials

### Test Connection:
```bash
ssh root@your-vps-ip
# Or with username:
ssh username@your-vps-ip
```

**Expected Output**: You should be in the VPS terminal

---

## STEP 2: Configure Your GoDaddy Domain DNS

### Important: Do This BEFORE You Finish Server Setup

1. **Log in to GoDaddy**: https://www.godaddy.com
2. Go to **My Products** → **Domains**
3. Click on your domain name
4. Click **Manage DNS**

### Update DNS Records:

**A Record (points your domain to VPS):**
- Host: `@`
- Type: `A`
- Value: **your-vps-ip-address** (from Step 1)
- TTL: `600` (or default)

**WWW Record (for www subdomain):**
- Host: `www`
- Type: `CNAME`
- Value: `yourdomain.com`
- TTL: `600` (or default)

**Save Changes**

⏳ **Wait 24-48 hours** for DNS to propagate (sometimes faster)

**Check DNS Status**:
```bash
nslookup yourdomain.com
# Should show your VPS IP
```

---

## STEP 3: Initial Server Setup (SSH into VPS)

```bash
# Connect to your VPS
ssh root@your-vps-ip
```

### 3.1 Update System
```bash
apt update
apt upgrade -y
```

### 3.2 Install Required Software
```bash
# Python and development tools
apt install -y python3 python3-pip python3-venv python3-dev build-essential

# PostgreSQL (Database)
apt install -y postgresql postgresql-contrib

# Nginx (Web Server)
apt install -y nginx

# SSL Certificate (Certbot)
apt install -y certbot python3-certbot-nginx

# Git
apt install -y git

# Text Editor
apt install -y nano
```

### 3.3 Create Application User
```bash
useradd -m -s /bin/bash bhrikuti
usermod -aG sudo bhrikuti
su - bhrikuti
```

---

## STEP 4: Setup PostgreSQL Database

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL terminal, run these commands:
```

Copy and paste these commands in PostgreSQL terminal:

```sql
CREATE DATABASE bhrikuti_db;
CREATE USER bhrikuti_user WITH PASSWORD 'choose-a-strong-password-here';
ALTER ROLE bhrikuti_user SET client_encoding TO 'utf8';
ALTER ROLE bhrikuti_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE bhrikuti_user SET default_transaction_deferrable TO on;
ALTER ROLE bhrikuti_user SET default_transaction_level TO 'read committed';
GRANT ALL PRIVILEGES ON DATABASE bhrikuti_db TO bhrikuti_user;
\q
```

**Save your database password** - you'll need it in Step 5!

---

## STEP 5: Clone and Setup Your Project

```bash
# Go to bhrikuti user home
cd /home/bhrikuti

# Clone your GitHub repository
git clone https://github.com/krishnadhakal03/bhrikutimandap.git
cd bhrikutimandap

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## STEP 6: Create .env File with Your Secrets

```bash
# Create .env file
nano .env
```

Copy this template and replace values:

```
DJANGO_SECRET_KEY=generate-a-secret-key-here
DJANGO_DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-vps-ip

DATABASE_ENGINE=postgresql
DATABASE_NAME=bhrikuti_db
DATABASE_USER=bhrikuti_user
DATABASE_PASSWORD=your-database-password
DATABASE_HOST=localhost
DATABASE_PORT=5432

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

SITE_URL=https://yourdomain.com
```

**To save:**
- Press `Ctrl+X`
- Press `Y` (yes)
- Press `Enter`

### Generate Django Secret Key:
```bash
python manage.py shell
```

In Python shell:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
# Copy the output and use it in .env
exit()
```

---

## STEP 7: Initialize Django Application

```bash
# Make sure venv is activated
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
# Follow prompts to create admin account

# Collect static files
python manage.py collectstatic --noinput
```

### Fix Permissions
```bash
sudo chown -R bhrikuti:bhrikuti /home/bhrikuti/bhrikutimandap
chmod -R 755 /home/bhrikuti/bhrikutimandap
```

---

## STEP 8: Setup Gunicorn (Application Server)

### 8.1 Create Gunicorn Service File
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Copy and paste:

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

Save: `Ctrl+X`, `Y`, `Enter`

### 8.2 Enable and Start Gunicorn
```bash
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn
```

**Expected Output**: Should show "active (running)"

---

## STEP 9: Setup Nginx (Web Server)

### 9.1 Create Nginx Config
```bash
sudo nano /etc/nginx/sites-available/bhrikutimandap
```

Copy and paste:

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
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/bhrikuti/bhrikutimandap/media/;
        expires 7d;
    }
}
```

Save: `Ctrl+X`, `Y`, `Enter`

### 9.2 Enable and Test Nginx
```bash
sudo ln -s /etc/nginx/sites-available/bhrikutimandap /etc/nginx/sites-enabled/
sudo nginx -t
```

**Expected Output**: "test is successful"

### 9.3 Restart Nginx
```bash
sudo systemctl restart nginx
```

---

## STEP 10: Setup SSL/HTTPS Certificate

⚠️ **Important**: Make sure DNS is propagated first (Step 2)

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

**Follow the prompts:**
- Enter your email
- Agree to terms
- Choose to redirect HTTP to HTTPS (option 2)

**Expected Output**: Certificate installed and auto-renewal configured

---

## STEP 11: Verify Everything Works

### Test Your Website:
1. Open browser: `https://yourdomain.com`
2. You should see your Bhrikutimandap website
3. Check `/admin/` to verify admin panel works

### Verify Services:
```bash
# Check all services
sudo systemctl status gunicorn
sudo systemctl status nginx
sudo systemctl status postgresql

# View logs for any errors
sudo journalctl -u gunicorn -n 20
```

---

## STEP 12: Setup Auto-Renewal for SSL

```bash
sudo certbot renew --dry-run
# Should succeed without errors
```

---

## QUICK REFERENCE COMMANDS

### Connect to VPS:
```bash
ssh root@your-vps-ip
su - bhrikuti
cd /home/bhrikuti/bhrikutimandap
source venv/bin/activate
```

### Restart Application:
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### View Logs:
```bash
sudo journalctl -u gunicorn -f
sudo tail -f /var/log/nginx/error.log
```

### Pull Latest Code:
```bash
cd /home/bhrikuti/bhrikutimandap
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

### Backup Database:
```bash
sudo -u postgres pg_dump bhrikuti_db > ~/backup_$(date +%Y%m%d_%H%M%S).sql
```

---

## TROUBLESHOOTING

### Domain not loading?
- Check DNS: `nslookup yourdomain.com`
- Wait 24-48 hours for DNS propagation
- Check Nginx: `sudo nginx -t`
- Check Gunicorn: `sudo systemctl status gunicorn`

### Static files not loading?
```bash
cd /home/bhrikuti/bhrikutimandap
python manage.py collectstatic --noinput --clear
sudo systemctl restart nginx
```

### Gunicorn errors?
```bash
sudo systemctl restart gunicorn
sudo journalctl -u gunicorn -n 50
```

### Database connection error?
- Check .env file has correct DATABASE_PASSWORD
- Verify PostgreSQL running: `sudo systemctl status postgresql`
- Restart PostgreSQL: `sudo systemctl restart postgresql`

### SSL certificate issues?
```bash
sudo certbot renew --force-renewal
sudo systemctl restart nginx
```

---

## SUMMARY OF CHANGES MADE

✅ **Production Release (committed to GitHub)**

1. **market/settings.py**:
   - Added environment variable support
   - PostgreSQL configuration
   - Security headers (SSL, HSTS, etc.)
   - Static files optimization with WhiteNoise

2. **requirements.txt**:
   - Added PostgreSQL driver (psycopg2-binary)
   - Added WhiteNoise for static files
   - Production-ready versions

3. **.env.example**:
   - Template for production environment variables
   - (Actual .env is in .gitignore for security)

---

## NEXT STEPS

1. ✅ Get VPS IP and SSH access from Hostinger
2. ✅ Update DNS on GoDaddy with VPS IP
3. ✅ Follow Steps 1-12 above
4. ✅ Test at `https://yourdomain.com`
5. ✅ Create superuser and log in to `/admin/`
6. ✅ Monitor with: `sudo journalctl -u gunicorn -f`

---

## SUPPORT

**Need help?** Check:
- Django Docs: https://docs.djangoproject.com/
- Gunicorn Docs: https://gunicorn.org/
- Nginx Docs: https://nginx.org/
- Let's Encrypt: https://letsencrypt.org/

**Status**: Ready for production deployment! 🚀
