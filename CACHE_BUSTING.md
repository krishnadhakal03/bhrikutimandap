# Cache Busting Strategy

## Problem
After CSS/HTML changes are deployed to production, browsers cache the old files. This requires users to clear their browser cache or use incognito mode to see the latest changes.

## Solution: Content-Hash Based Cache Busting

We use Django's **ManifestStaticFilesStorage** (via WhiteNoise's `CompressedManifestStaticFilesStorage`) to automatically append a content hash to static file names.

### How It Works

1. **On Deployment (`collectstatic`)**
   - During `python manage.py collectstatic`, Django computes a hash of each static file's content
   - Original file: `static/admin/css/bhrikutimandap-admin.css`
   - Hashed file: `staticfiles/admin/css/bhrikutimandap-admin.12345abcde.css`
   - A manifest file (`staticfiles/manifest.json`) maps original names to hashed names

2. **In Templates**
   - Instead of hardcoding URLs, use the `{% static %}` template tag:
     ```html
     <!-- ✓ Correct (uses cache busting) -->
     <link rel="stylesheet" href="{% static 'admin/css/bhrikutimandap-admin.css' %}">
     
     <!-- ✗ Avoid (won't use cache busting) -->
     <link rel="stylesheet" href="/static/admin/css/bhrikutimandap-admin.css">
     ```
   - Django replaces the tag with the hashed filename

3. **Browser Behavior**
   - When you push CSS changes → hash changes → filename changes
   - Browsers see a "new" file URL → fetch fresh copy
   - No need for users to clear cache!

## CICD Integration

Your current CICD flow already handles this:

```yaml
# Deploy step in .github/workflows/ci-cd.yml
$COMPOSE --env-file .env.prod -f compose.prod.yml exec -T web python manage.py collectstatic --noinput
```

This runs on **every deployment**, automatically regenerating hashes for changed files.

## Configuration

In `market/settings.py`:

```python
# Production: Use manifest storage for cache busting
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
else:
    # Development: standard storage (no hashing)
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
```

## Long-Term Cache Headers

Additionally, configure your web server to set long cache expiration headers:

### Nginx (already reverse-proxying your app)
```nginx
# Add to your nginx config (e.g., `/etc/nginx/sites-available/bhrikutimandap`)
location ~ ^/static/ {
    # Cache hashed static files for 1 year (they won't change due to hash)
    expires 365d;
    add_header Cache-Control "public, immutable";
    access_log off;
}

location ~ ^/media/ {
    # Cache media files for 30 days
    expires 30d;
    add_header Cache-Control "public";
}

location / {
    # Don't cache HTML (it changes more frequently)
    add_header Cache-Control "no-cache, must-revalidate";
}
```

## What Happens on Deployment

1. Push CSS/HTML changes to GitHub
2. GitHub Actions deploys to VPS
3. Deploy runs: `python manage.py collectstatic`
4. Django hashes all files:
   - `bhrikutimandap-admin.css` → `bhrikutimandap-admin.a1b2c3d4e5f6.css` (new hash)
5. Browsers see new URL → fetch fresh version
6. No manual cache clearing needed! ✓

## Testing Locally

To test cache busting locally:

```bash
# Enable manifest storage temporarily
export DEBUG=False

# Collect static files
python manage.py collectstatic --noinput

# Check generated manifest
cat staticfiles/manifest.json

# Run development server
python manage.py runserver
```

You should see hashed filenames in:
- Network tab (DevTools)
- Generated HTML (view source)

Then update a CSS file and run `collectstatic` again—the hash should change.

## Troubleshooting

### Issue: `{% static %}` tag not updating
- **Cause**: Not using the template tag in templates
- **Fix**: Replace hardcoded paths with `{% load static %}` and `{% static 'path/to/file' %}`

### Issue: Changes not showing in production
- **Cause**: Deploy didn't run `collectstatic`
- **Fix**: Ensure CICD workflow includes the collectstatic step (it does by default)

### Issue: Hashes don't change after CSS update
- **Cause**: File not actually modified (whitespace, comments, etc.)
- **Fix**: Make substantive changes; whitespace affects the hash

## Benefits

✓ **No manual cache clearing needed**
✓ **Users always get latest version**
✓ **Reduces support requests**
✓ **Can set aggressive cache headers** (files won't change unless hash changes)
✓ **Zero-downtime deployments** (old and new versions can coexist briefly)
