"""
Custom email backend that uses dynamic SMTP configuration from SiteSettings.
"""

from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class DynamicSMTPBackend(EmailBackend):
    """
    SMTP backend that loads credentials from SiteSettings at runtime.
    Allows changing email configuration without restarting the server.
    """

    def __init__(self, fail_silently=False):
        try:
            # Import here to avoid circular dependency
            from store.models import SiteSettings
            
            site_settings = SiteSettings.get_instance()
            
            # Use SiteSettings values if available, otherwise fall back to Django settings
            host = site_settings.email_host or settings.EMAIL_HOST
            port = site_settings.email_port or settings.EMAIL_PORT
            username = site_settings.email_host_user or settings.EMAIL_HOST_USER
            password = site_settings.email_host_password or settings.EMAIL_HOST_PASSWORD
            use_tls = site_settings.email_use_tls
            
            logger.debug(f"DynamicSMTPBackend initialized with host={host}, port={port}, user={username}")
            
        except Exception as e:
            # Fallback to Django settings if SiteSettings is not available
            logger.warning(f"Could not load SiteSettings for email config: {e}. Using Django settings.")
            host = settings.EMAIL_HOST
            port = settings.EMAIL_PORT
            username = settings.EMAIL_HOST_USER
            password = settings.EMAIL_HOST_PASSWORD
            use_tls = settings.EMAIL_USE_TLS
        
        super().__init__(
            host=host,
            port=port,
            username=username,
            password=password,
            use_tls=use_tls,
            fail_silently=fail_silently,
        )
