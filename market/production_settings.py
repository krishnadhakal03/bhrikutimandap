"""
Production settings for Bhrikutimandap Django project.

This file contains production-specific settings that override the base settings.
It should be used when deploying to Hostinger or any production environment.

To use these settings, set the DJANGO_SETTINGS_MODULE environment variable:
    export DJANGO_SETTINGS_MODULE=market.production_settings

Or pass it as a command line argument:
    python manage.py runserver --settings=market.production_settings
"""

from .settings import *
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', '0') == '1'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable is not set")

# ALLOWED_HOSTS must include your domain name
DOMAIN_NAME = os.getenv('DOMAIN_NAME', '')
if not DOMAIN_NAME:
    raise ValueError("DOMAIN_NAME environment variable is not set")

ALLOWED_HOSTS = [
    DOMAIN_NAME,
    f'www.{DOMAIN_NAME}',
]

# Database Configuration
# Using MySQL for production (recommended for Hostinger)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Validate database configuration
if not all([
    os.getenv('DB_NAME'),
    os.getenv('DB_USER'),
    os.getenv('DB_PASSWORD')
]):
    raise ValueError("Database environment variables (DB_NAME, DB_USER, DB_PASSWORD) must be set")

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# WhiteNoise configuration for serving static files efficiently
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security Settings
SECURE_SSL_REDIRECT = True  # Redirect all HTTP to HTTPS
SESSION_COOKIE_SECURE = True  # Only send session cookie over HTTPS
CSRF_COOKIE_SECURE = True  # Only send CSRF cookie over HTTPS
SECURE_BROWSER_XSS_FILTER = True  # Enable browser XSS protection
SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME type sniffing
X_FRAME_OPTIONS = 'DENY'  # Prevent clickjacking
SECURE_HSTS_SECONDS = 31536000  # Enable HSTS for 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Email Configuration (optional)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.hostinger.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', f'noreply@{DOMAIN_NAME}')

# Site URL (used in activation links, etc.)
SITE_URL = os.getenv('SITE_URL', f'https://{DOMAIN_NAME}')

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django_errors.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Cache Configuration (optional - for better performance)
# Uncomment to use cache
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
#         'LOCATION': 'cache_table',
#     }
# }
# Run: python manage.py createcachetable

# Session Configuration
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_NAME = 'bhrikutimandap_sessionid'

# CSRF Configuration
CSRF_COOKIE_HTTPONLY = False  # Must be False for AJAX requests
CSRF_COOKIE_NAME = 'bhrikutimandap_csrftoken'
CSRF_TRUSTED_ORIGINS = [
    f'https://{DOMAIN_NAME}',
    f'https://www.{DOMAIN_NAME}',
]

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# Admin Configuration
ADMINS = [
    ('Admin', os.getenv('ADMIN_EMAIL', f'admin@{DOMAIN_NAME}')),
]
MANAGERS = ADMINS

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = os.getenv('TIME_ZONE', 'Asia/Kathmandu')  # Nepal timezone
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Performance optimizations
CONN_MAX_AGE = 600  # Keep database connections alive for 10 minutes

# Custom settings for the application
# Add any custom application-specific settings here
