# 📋 Hostinger Deployment Checklist

Use this checklist to ensure you complete all necessary steps when deploying Bhrikutimandap to Hostinger.

## Pre-Deployment

- [ ] Hostinger account created (Premium/Business or VPS plan)
- [ ] Domain name registered and pointed to Hostinger nameservers
- [ ] Local application tested and working
- [ ] All dependencies listed in `requirements.txt`
- [ ] Git repository is up to date

## Configuration Files

- [ ] `passenger_wsgi.py` created in project root
- [ ] `.htaccess` created and configured (update username paths)
- [ ] `market/production_settings.py` created
- [ ] `.env` file created (copy from `.env.example`)
- [ ] Generated new `DJANGO_SECRET_KEY`
- [ ] Updated domain name in `.env`
- [ ] Updated username paths in `passenger_wsgi.py`
- [ ] Updated username paths in `.htaccess`

## Database Setup

- [ ] MySQL database created in Hostinger hPanel
- [ ] Database credentials added to `.env` file
- [ ] Database connection tested
- [ ] Production database settings configured

## File Upload

- [ ] Project uploaded to `~/public_html/bhrikutimandap/` via Git or FTP
- [ ] Virtual environment created: `python3 -m venv venv`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] File permissions set correctly
- [ ] `.env` file permissions set to 600

## Django Setup

- [ ] Migrations run: `python manage.py migrate --settings=market.production_settings`
- [ ] Superuser created: `python manage.py createsuperuser --settings=market.production_settings`
- [ ] Static files collected: `python manage.py collectstatic --settings=market.production_settings`
- [ ] (Optional) Sample data loaded: `python manage.py seed --settings=market.production_settings`

## Security

- [ ] `DEBUG = False` in production settings
- [ ] Strong `SECRET_KEY` generated and set
- [ ] `ALLOWED_HOSTS` configured with domain name
- [ ] SSL certificate installed (HTTPS enabled)
- [ ] Security headers configured in `.htaccess`
- [ ] Sensitive files protected (`.env`, `db.sqlite3`)
- [ ] Database credentials secured

## Testing

- [ ] Homepage accessible: `https://yourdomain.com`
- [ ] Admin panel accessible: `https://yourdomain.com/admin/`
- [ ] Can log in to admin panel
- [ ] Static files loading correctly (CSS, JS, images)
- [ ] Media uploads working
- [ ] Agent dashboard accessible: `https://yourdomain.com/agent/dashboard/`
- [ ] Customer registration working
- [ ] All main features tested

## Post-Deployment

- [ ] Application restarted: `touch tmp/restart.txt`
- [ ] Error logs checked for issues
- [ ] Database backup configured
- [ ] Regular backup schedule set up
- [ ] Monitoring tools configured (optional)
- [ ] Email configuration tested (optional)

## Maintenance Setup

- [ ] Backup script created and scheduled
- [ ] Log rotation configured
- [ ] Monitoring alerts set up
- [ ] Update procedure documented
- [ ] Emergency contacts list created

## Documentation

- [ ] Deployment details documented
- [ ] Credentials stored securely (password manager)
- [ ] Server access information saved
- [ ] Database connection details saved
- [ ] Team members notified of deployment

## Optional Enhancements

- [ ] CDN configured for static files
- [ ] Email service configured (SendGrid, Mailgun, etc.)
- [ ] Monitoring service added (Sentry, New Relic, etc.)
- [ ] Performance optimization applied
- [ ] Caching configured
- [ ] Analytics added (Google Analytics, etc.)

---

## Quick Command Reference

```bash
# SSH into Hostinger
ssh username@yourdomain.com

# Navigate to project
cd ~/public_html/bhrikutimandap

# Activate virtual environment
source venv/bin/activate

# Run migrations
python manage.py migrate --settings=market.production_settings

# Collect static files
python manage.py collectstatic --noinput --settings=market.production_settings

# Create superuser
python manage.py createsuperuser --settings=market.production_settings

# Restart application
touch tmp/restart.txt

# View error logs (if available)
tail -f logs/django_errors.log
```

---

## Troubleshooting Checklist

If something isn't working:

- [ ] Check error logs
- [ ] Verify environment variables in `.env`
- [ ] Confirm database connection
- [ ] Check file permissions
- [ ] Verify `ALLOWED_HOSTS` includes domain
- [ ] Ensure virtual environment is activated
- [ ] Check Python version compatibility
- [ ] Verify all dependencies installed
- [ ] Restart application: `touch tmp/restart.txt`
- [ ] Clear browser cache
- [ ] Check DNS propagation

---

**Need Help?**
- 📖 See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions
- 🐛 Check [ISSUES_FOUND.md](ISSUES_FOUND.md) for known issues
- 💬 Create an issue on GitHub

---

**Deployment Checklist Version:** 1.0  
**Last Updated:** December 22, 2024
