import os
import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
if os.path.exists(BASE_DIR / '.env'):
    try:
        import importlib

        dotenv = importlib.import_module('dotenv')
        dotenv.load_dotenv(BASE_DIR / '.env')
    except Exception:
        pass

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-secret-key-change-this-in-production')
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

# Make the test environment behave like development (avoid SSL redirects, etc.)
if 'test' in sys.argv:
    DEBUG = True

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if host.strip()
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ckeditor',
    'ckeditor_uploader',
    'widget_tweaks',
    'store',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'market.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_processors.site_settings',
                'store.context_processors.cart_count',
                'store.context_processors.categories',
            ],
        },
    },
]

WSGI_APPLICATION = 'market.wsgi.application'

# Database
if os.environ.get('DATABASE_ENGINE') == 'postgresql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DATABASE_NAME', 'bhrikuti_db'),
            'USER': os.environ.get('DATABASE_USER', 'bhrikuti_user'),
            'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
            'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
            'PORT': os.environ.get('DATABASE_PORT', '5432'),
        }
    }
else:
    # Use SQLite by default for local development and quick testing.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Media (product images)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Add store context processors
TEMPLATES[0]['OPTIONS']['context_processors'].append('store.context_processors.cart_count')
TEMPLATES[0]['OPTIONS']['context_processors'].append('store.context_processors.static_version')
TEMPLATES[0]['OPTIONS']['context_processors'].append('store.context_processors.site_settings')
TEMPLATES[0]['OPTIONS']['context_processors'].append('store.context_processors.categories')
TEMPLATES[0]['OPTIONS']['context_processors'].append('store.context_processors.dynamic_pages')

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'store.validators.ComplexPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication
AUTH_USER_MODEL = 'store.User'

# Security / proxy settings (disabled in development to prevent SSL issues)
if DEBUG:
    SECURE_PROXY_SSL_HEADER = None
else:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
USE_X_FORWARDED_HOST = not DEBUG

# Security settings for production (disabled in development)
SECURE_SSL_REDIRECT = (not DEBUG) and (os.environ.get('SECURE_SSL_REDIRECT', 'True') == 'True')
SESSION_COOKIE_SECURE = (not DEBUG) and (os.environ.get('SESSION_COOKIE_SECURE', 'True') == 'True')
CSRF_COOKIE_SECURE = (not DEBUG) and (os.environ.get('CSRF_COOKIE_SECURE', 'True') == 'True')

# HSTS settings (disabled in development to avoid browser caching issues)
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '0' if DEBUG else '31536000'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = (not DEBUG)
SECURE_HSTS_PRELOAD = (not DEBUG)
SECURE_REFERRER_POLICY = 'same-origin' if not DEBUG else None

# CSRF trusted origins (required when using HTTPS and a real domain)
_default_csrf_trusted = ''
if not DEBUG:
    _default_csrf_trusted = 'https://bhrikutimandap.com,https://www.bhrikutimandap.com'
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get('CSRF_TRUSTED_ORIGINS', _default_csrf_trusted).split(',')
    if origin.strip()
]

# WhiteNoise for static files (simple production setup behind Nginx)
if not DEBUG:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    # Use compressed static files storage
    # Cache busting is handled via HTTP headers (set in Nginx) and version parameter in templates
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
else:
    # Development: use default static files storage
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Static files version for cache busting (update this on each deployment)
# Use in templates as: {% static 'file.css' %}?v={{ STATIC_VERSION }}
STATIC_VERSION = os.environ.get('STATIC_VERSION', '1.0')

# Email backend
import sys
if 'test' in sys.argv:
    EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
elif DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # For production, use SMTP with dynamic configuration
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    # Email settings will be applied dynamically in views via get_email_config()
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'no-reply@bhrikutimandap.com')
CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL', 'admin@bhrikutimandap.com')

# CKEditor Configuration
CKEDITOR_BASEPATH = '/static/ckeditor/ckeditor/'
CKEDITOR_UPLOAD_PATH = 'uploads/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 400,
        'width': '100%',
        'toolbar_Custom': [
            ['Styles', 'Format', 'Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Table', '-', 'HorizontalRule'],
            ['Source'],
            ['Maximize']
        ],
        'toolbar': 'Custom',
        'extraPlugins': ','.join(['uploadimage', 'div', 'autolink', 'autoembed', 'embedsemantic', 'autogrow', 'widget', 'lineutils', 'clipboard', 'widgetselection', 'elementspath']),
    }
}

# Site URL used in activation links
SITE_URL = os.environ.get('SITE_URL', 'http://127.0.0.1:8000')
