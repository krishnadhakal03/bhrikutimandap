# Hostinger Deployment - Copy & Paste Commands

**Use these exact commands in order. Copy, paste into SSH terminal, press Enter.**

---

## BEFORE YOU START

You need:
- [ ] VPS IP address (from Hostinger)
- [ ] SSH username (usually "root")
- [ ] SSH password (from Hostinger)
- [ ] Your domain name
- [ ] A strong password for PostgreSQL

---

## STEP 1: Connect to VPS

Open your terminal/PowerShell and run:

```bash
ssh root@YOUR_VPS_IP_HERE
```

Replace `YOUR_VPS_IP_HERE` with actual IP (e.g., `192.168.1.100`)

When asked "Are you sure you want to continue?", type: `yes`

Enter password when prompted.

**Expected**: You see a terminal prompt like `root@vps-12345:~#`

---

## STEP 2: Update System

Copy and paste each command one by one:

```bash
apt update
```

Wait for it to finish. Then:

```bash
apt upgrade -y
```

Wait for completion.

---

## STEP 3: Install Required Software

Copy and paste this entire block (all at once is fine):

```bash
apt install -y python3 python3-pip python3-venv python3-dev build-essential postgresql postgresql-contrib nginx certbot python3-certbot-nginx git nano
```

Wait for completion (might take 2-5 minutes).

---

## STEP 4: Create Application User

```bash
useradd -m -s /bin/bash bhrikuti
```

Then:

```bash
su - bhrikuti
```

**Expected**: Prompt changes to `bhrikuti@vps-12345:~$`

---

## STEP 5: Setup PostgreSQL Database

Run this command:

```bash
sudo -u postgres psql
```

**Expected**: You see `postgres=#` prompt

Now copy and paste **each line** (one at a time):

```sql
CREATE DATABASE bhrikuti_db;
```

```sql
CREATE USER bhrikuti_user WITH PASSWORD 'CHOOSE_A_STRONG_PASSWORD_HERE';
```

Replace `CHOOSE_A_STRONG_PASSWORD_HERE` with actual password (keep the quotes!)

```sql
ALTER ROLE bhrikuti_user SET client_encoding TO 'utf8';
```

```sql
ALTER ROLE bhrikuti_user SET default_transaction_isolation TO 'read committed';
```

```sql
ALTER ROLE bhrikuti_user SET default_transaction_deferrable TO on;
```

```sql
ALTER ROLE bhrikuti_user SET default_transaction_level TO 'read committed';
```

```sql
GRANT ALL PRIVILEGES ON DATABASE bhrikuti_db TO bhrikuti_user;
```

```sql
\q
```

**Expected**: Back to `bhrikuti@vps-12345:~$` prompt

---

## STEP 6: Clone Your Project

```bash
cd /home/bhrikuti
git clone https://github.com/krishnadhakal03/bhrikutimandap.git
cd bhrikutimandap
```

---

## STEP 7: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

**Expected**: Prompt shows `(venv) bhrikuti@...`

---

## STEP 8: Install Python Packages

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Wait for completion (1-2 minutes).

---

## STEP 9: Generate Django Secret Key

```bash
python manage.py shell
```

**Expected**: Prompt shows `>>>`

Copy and paste:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

**You'll see something like**: `'abc123xyz...'`

**COPY THIS VALUE** (the entire quoted string)

Then:

```python
exit()
```

---

## STEP 10: Create .env File

```bash
nano .env
```

A text editor opens. Copy and paste this template:

```
DJANGO_SECRET_KEY=PASTE_YOUR_SECRET_KEY_HERE
DJANGO_DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,YOUR_VPS_IP_HERE

DATABASE_ENGINE=postgresql
DATABASE_NAME=bhrikuti_db
DATABASE_USER=bhrikuti_user
DATABASE_PASSWORD=THE_PASSWORD_YOU_CHOSE_IN_STEP_5
DATABASE_HOST=localhost
DATABASE_PORT=5432

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

SITE_URL=https://yourdomain.com
```

**Replace:**
- `PASTE_YOUR_SECRET_KEY_HERE` → from Step 9
- `yourdomain.com` → your actual domain
- `YOUR_VPS_IP_HERE` → your VPS IP
- `THE_PASSWORD_YOU_CHOSE_IN_STEP_5` → PostgreSQL password from Step 5

Save: Press `Ctrl+X`, then `Y`, then `Enter`

---

## STEP 11: Run Django Migrations

```bash
python manage.py migrate
```

Wait for completion.

---

## STEP 12: Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts:
- **Username**: admin (or your choice)
- **Email**: your-email@example.com
- **Password**: Something strong (won't show as you type)
- **Confirm**: Retype password

---

## STEP 13: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

Wait for completion.

---

## STEP 14: Fix File Permissions

```bash
sudo chown -R bhrikuti:bhrikuti /home/bhrikuti/bhrikutimandap
chmod -R 755 /home/bhrikuti/bhrikutimandap
```

---

## STEP 15: Create Gunicorn Service

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Copy and paste this entire block:

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

Save: Press `Ctrl+X`, then `Y`, then `Enter`

---

## STEP 16: Start Gunicorn

```bash
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn
```

**Expected**: Shows "active (running)"

---

## STEP 17: Create Nginx Config

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

**Replace**: `yourdomain.com` with your actual domain

Save: Press `Ctrl+X`, then `Y`, then `Enter`

---

## STEP 18: Enable Nginx

```bash
sudo ln -s /etc/nginx/sites-available/bhrikutimandap /etc/nginx/sites-enabled/
sudo nginx -t
```

**Expected**: Shows "test is successful"

---

## STEP 19: Restart Nginx

```bash
sudo systemctl restart nginx
```

---

## STEP 20: Setup SSL Certificate

**IMPORTANT: Make sure DNS is updated in GoDaddy first!**

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

**Replace**: `yourdomain.com` with your domain

Follow prompts:
- Enter your email
- Agree to terms (type `Y`)
- Choose redirect option (type `2` for HTTPS redirect)

**Expected**: "Congratulations! Your certificate has been installed"

---

## STEP 21: Verify Everything Works

```bash
sudo systemctl status gunicorn
sudo systemctl status nginx
sudo systemctl status postgresql
```

All three should show "active (running)"

---

## STEP 22: Test Your Website

Open your browser and go to:

```
https://yourdomain.com
```

You should see your website!

---

## Testing Admin Panel

Go to:

```
https://yourdomain.com/admin/
```

Log in with superuser credentials from Step 12.

---

## If Something Goes Wrong

### Check Gunicorn Errors:
```bash
sudo journalctl -u gunicorn -n 50
```

### Check Nginx Errors:
```bash
sudo tail -f /var/log/nginx/error.log
```

### Restart Everything:
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### Check Permissions:
```bash
sudo chown -R bhrikuti:www-data /home/bhrikuti/bhrikutimandap
```

---

## Important Reminders

1. **DNS**: Wait 24-48 hours after updating GoDaddy DNS
2. **Passwords**: Make them strong and unique
3. **.env**: Never commit this file (it's in .gitignore)
4. **Superuser**: Remember the username and password you created
5. **Backups**: Your original SQLite database stays on your local machine

---

## Update Your Website Later

When you push new code to GitHub:

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

## All Set! 🎉

Your website is now live at `https://yourdomain.com`

Refer to [HOSTINGER_GODADDY_SETUP.md](HOSTINGER_GODADDY_SETUP.md) for detailed explanations of each step.
