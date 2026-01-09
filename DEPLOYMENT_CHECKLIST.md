# Production Deployment Checklist

## PHASE 1: Local Machine (✅ COMPLETED)

- [x] Updated `market/settings.py` for production
- [x] Added PostgreSQL database configuration
- [x] Added security headers (SSL, HSTS, etc.)
- [x] Updated `requirements.txt` with production packages
- [x] Created `.env.example` file
- [x] Committed all changes to GitHub
- [x] Pushed to main branch

---

## PHASE 2: Hostinger VPS Setup

### Pre-Deployment (DO THIS FIRST)

- [ ] Get VPS IP address from Hostinger
- [ ] Get SSH credentials from Hostinger
- [ ] Update GoDaddy DNS A record to point to VPS IP
- [ ] Wait 24-48 hours for DNS propagation
- [ ] Test DNS: `nslookup yourdomain.com`

### Server Installation (Steps 1-5 in HOSTINGER_GODADDY_SETUP.md)

- [ ] SSH into VPS: `ssh root@your-vps-ip`
- [ ] Update system packages
- [ ] Install Python, PostgreSQL, Nginx, Certbot, Git
- [ ] Create `bhrikuti` user
- [ ] Create PostgreSQL database and user
- [ ] Clone GitHub repository
- [ ] Create Python virtual environment
- [ ] Install Python dependencies from requirements.txt

### Application Setup (Steps 6-7)

- [ ] Create `.env` file with your secrets
- [ ] Generate Django SECRET_KEY
- [ ] Run `python manage.py migrate`
- [ ] Create superuser account
- [ ] Run `python manage.py collectstatic --noinput`
- [ ] Fix file permissions

### Gunicorn Setup (Step 8)

- [ ] Create `/etc/systemd/system/gunicorn.service`
- [ ] Start and enable Gunicorn
- [ ] Verify Gunicorn is running

### Nginx Setup (Step 9)

- [ ] Create `/etc/nginx/sites-available/bhrikutimandap`
- [ ] Enable Nginx site
- [ ] Test Nginx configuration
- [ ] Restart Nginx

### SSL Certificate (Step 10)

- [ ] Run Certbot to generate SSL certificate
- [ ] Verify HTTPS works
- [ ] Confirm auto-renewal is setup

---

## PHASE 3: Verification

- [ ] Visit `https://yourdomain.com` in browser
- [ ] Check website loads correctly
- [ ] Access `/admin/` and verify it works
- [ ] Check all services running: `sudo systemctl status gunicorn`, `nginx`, `postgresql`
- [ ] Verify logs for any errors: `sudo journalctl -u gunicorn -n 20`
- [ ] Test static files load (CSS, images, etc.)
- [ ] Test media files upload/download

---

## PHASE 4: Security & Maintenance

- [ ] Review `.env` file - ensure all secrets are strong
- [ ] Disable root login via SSH (optional security measure)
- [ ] Setup firewall rules (optional)
- [ ] Configure automatic backups of database
- [ ] Setup log monitoring
- [ ] Test update process for pulling new code

---

## CRITICAL INFORMATION TO HAVE READY

Before you start, gather:

- [ ] **VPS IP Address**: ________________
- [ ] **VPS SSH Username**: ________________
- [ ] **VPS SSH Password**: ________________
- [ ] **Domain Name**: ________________
- [ ] **Database Password**: ________________
- [ ] **Django SECRET_KEY**: ________________
- [ ] **Email for SSL**: ________________

---

## COMMAND SUMMARY

### Connect to VPS:
```bash
ssh root@your-vps-ip
su - bhrikuti
cd /home/bhrikuti/bhrikutimandap
```

### Activate Environment:
```bash
source venv/bin/activate
```

### View Status:
```bash
sudo systemctl status gunicorn
sudo systemctl status nginx
sudo systemctl status postgresql
```

### View Logs:
```bash
sudo journalctl -u gunicorn -f
```

### Update Application:
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

## FILES TO REFERENCE

1. **HOSTINGER_GODADDY_SETUP.md** - Step-by-step deployment guide
2. **DEPLOYMENT_GUIDE.md** - Detailed technical documentation
3. **market/settings.py** - Django production configuration
4. **requirements.txt** - Python dependencies
5. **.env.example** - Environment variables template

---

## POST-DEPLOYMENT TASKS

After your site is live:

1. **Monitor**: Watch logs for errors
2. **Backup**: Create database backup
3. **Test**: Verify all features work
4. **Email**: Configure email service (Gmail, SendGrid, etc.)
5. **Analytics**: Setup website analytics if needed
6. **Monitoring**: Setup uptime monitoring
7. **Updates**: Plan regular Django/package updates

---

**Status**: Ready to deploy! 🚀

**Start with Step 1 in HOSTINGER_GODADDY_SETUP.md**
