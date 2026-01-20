# Cache Busting Strategy

## Problem
After CSS/HTML changes are deployed to production, browsers cache the old files. This requires users to clear their browser cache or use incognito mode to see the latest changes.

## Solution: Version-Based Cache Busting

We use a simple **version parameter** approach that automatically increments on each deployment. This forces browsers to fetch fresh static files without modifying filenames.

### How It Works

1. **On Deployment**
   - CICD generates a unique `STATIC_VERSION` using the deployment timestamp
   - Version is stored in `.env.prod` and passed to Django settings
   - Example: `STATIC_VERSION=1.1705801547` (version 1 + unix timestamp)

2. **In Templates**
   - Use the `{% static %}` template tag (always do this!):
     ```html
     <!-- ✓ Correct (uses cache busting) -->
     <link rel="stylesheet" href="{% static 'admin/css/bhrikutimandap-admin.css' %}?v={{ STATIC_VERSION }}">
     <script src="{% static 'js/main.js' %}?v={{ STATIC_VERSION }}"></script>
     
     <!-- ✗ Avoid (won't use cache busting) -->
     <link rel="stylesheet" href="/static/admin/css/bhrikutimandap-admin.css">
     ```
   - The version parameter forces browsers to treat updated files as new

3. **Browser Behavior**
   - When you push CSS changes → deployment increments version
   - URL changes: `/static/style.css?v=1.1705801234` → `/static/style.css?v=1.1705801547`
   - Browsers see different URL → fetch fresh copy
   - No manual cache clearing needed!

## CICD Integration

Your CICD workflow automatically handles this:

```yaml
# Deploy step in .github/workflows/ci-cd.yml

# Run migrations and collectstatic
$COMPOSE --env-file .env.prod -f compose.prod.yml exec -T web python manage.py migrate
$COMPOSE --env-file .env.prod -f compose.prod.yml exec -T web python manage.py collectstatic --noinput

# Cache busting: increment version on each deployment
CURRENT_VERSION=$(grep "^STATIC_VERSION=" .env.prod 2>/dev/null || echo "STATIC_VERSION=1.0")
TIMESTAMP=$(date +%s)
echo "STATIC_VERSION=1.$(($TIMESTAMP))" >> .env.prod
echo "Cache busting version updated: 1.$TIMESTAMP"
```

## Configuration

In `market/settings.py`:

```python
# Static files version for cache busting
# Automatically set by CICD on each deployment
STATIC_VERSION = os.environ.get('STATIC_VERSION', '1.0')
```

Pass to templates via context processor:

```python
# In store/context_processors.py or similar
def static_version(request):
    return {'STATIC_VERSION': settings.STATIC_VERSION}
```

## Why This Approach?

✓ **Simple**: Just add `?v=VERSION` to URLs
✓ **Robust**: Works with any CSS/static file structure
✓ **No filename changes**: Avoids manifest file issues
✓ **Automatic**: Increments on every deployment
✓ **Reliable**: Works across all browsers and CDNs

## HTTP Cache Headers (Nginx)

For even better performance, configure long cache expiration headers:

```nginx
# Add to your nginx config (e.g., `/etc/nginx/sites-available/bhrikutimandap`)
location ~ ^/static/ {
    # Cache static files for 30 days since they change with version parameter
    expires 30d;
    add_header Cache-Control "public, must-revalidate";
    access_log off;
}

location ~ ^/media/ {
    # Cache media for 7 days
    expires 7d;
    add_header Cache-Control "public, must-revalidate";
}

location / {
    # Don't cache HTML (it changes more frequently)
    add_header Cache-Control "no-cache, must-revalidate";
}
```

## What Happens on Deployment

1. Push CSS/HTML changes to GitHub
2. GitHub Actions deploys to VPS
3. Deploy runs: `collectstatic` and increments `STATIC_VERSION`
   - Old version: `?v=1.1705801234`
   - New version: `?v=1.1705801547`
4. Browsers see new URL → fetch fresh version
5. No manual cache clearing needed! ✓

## Testing Locally

To test cache busting locally:

```bash
# Set a version manually
export STATIC_VERSION=1.1234567890

# Run development server
python manage.py runserver

# Check that the version appears in generated HTML
# View source in browser and search for ?v=
```

Update the version and refresh—you should see the new parameter in the HTML.

## Troubleshooting

### Issue: Version parameter not appearing in HTML
- **Cause**: Not using the template tag or context processor not added
- **Fix**: Use `{% static 'file.css' %}?v={{ STATIC_VERSION }}` in templates
- **Fix**: Add context processor to pass `STATIC_VERSION` to all templates

### Issue: Changes not showing after deployment
- **Cause**: Old version still in browser cache
- **Fix**: Force refresh (Ctrl+Shift+R or Cmd+Shift+R)
- **Fix**: Deployment may not have completed; check logs

### Issue: Version parameter showing as empty
- **Cause**: `STATIC_VERSION` not set in environment
- **Fix**: Ensure `.env.prod` has `STATIC_VERSION=1.xxx` after deployment
- **Fix**: Check CICD deploy logs for errors

## Benefits

✓ **No manual cache clearing needed**
✓ **Users always get latest version**
✓ **Reduces support requests** ("Please refresh your browser")
✓ **Can set aggressive cache headers** (since version changes with updates)
✓ **Works reliably** across browsers, CDNs, and proxies
✓ **Simple to implement** and debug

