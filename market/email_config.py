"""
Dynamic email configuration helper.
Loads email settings from database (SiteSettings) with fallback to environment variables.
"""

import os
import logging

logger = logging.getLogger(__name__)


def get_email_config():
    """
    Get email configuration from SiteSettings or environment variables.
    Returns a dictionary with email settings.
    """
    try:
        # Avoid circular imports by importing here
        from store.models import SiteSettings
        
        settings = SiteSettings.get_instance()
        
        return {
            'EMAIL_HOST': settings.email_host or os.environ.get('EMAIL_HOST', 'localhost'),
            'EMAIL_PORT': settings.email_port or int(os.environ.get('EMAIL_PORT', '587')),
            'EMAIL_USE_TLS': settings.email_use_tls,
            'EMAIL_HOST_USER': settings.email_host_user or os.environ.get('EMAIL_HOST_USER', ''),
            'EMAIL_HOST_PASSWORD': settings.email_host_password or os.environ.get('EMAIL_HOST_PASSWORD', ''),
            'DEFAULT_FROM_EMAIL': settings.default_from_email or os.environ.get('DEFAULT_FROM_EMAIL', 'admin@bhrikutimandap.com'),
        }
    except Exception as e:
        # Fallback to environment variables if database is not available
        logger.debug(f"Could not load email config from database: {e}. Using environment variables.")
        return {
            'EMAIL_HOST': os.environ.get('EMAIL_HOST', 'localhost'),
            'EMAIL_PORT': int(os.environ.get('EMAIL_PORT', '587')),
            'EMAIL_USE_TLS': os.environ.get('EMAIL_USE_TLS', 'True') == 'True',
            'EMAIL_HOST_USER': os.environ.get('EMAIL_HOST_USER', ''),
            'EMAIL_HOST_PASSWORD': os.environ.get('EMAIL_HOST_PASSWORD', ''),
            'DEFAULT_FROM_EMAIL': os.environ.get('DEFAULT_FROM_EMAIL', 'admin@bhrikutimandap.com'),
        }
