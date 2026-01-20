from django.conf import settings
from .models import Cart, CartItem, SiteSettings


def cart_count(request):
    count = 0
    if request.user.is_authenticated:
        try:
            cart = request.user.cart
            count = sum(item.quantity for item in cart.items.all())
        except Cart.DoesNotExist:
            count = 0
    else:
        cart = request.session.get('cart', {})
        count = sum(cart.values())
    return {'cart_count': count}


def static_version(request):
    """Add STATIC_VERSION to all template contexts for cache busting."""
    return {'STATIC_VERSION': getattr(settings, 'STATIC_VERSION', '1.0')}


def site_settings(request):
    """Add SiteSettings singleton to all template contexts."""
    try:
        from django.db import connection
        from django.db.utils import OperationalError
        
        # Check if table exists
        with connection.cursor() as cursor:
            try:
                cursor.execute("SELECT 1 FROM store_sitesettings LIMIT 1")
            except OperationalError:
                # Table doesn't exist yet
                return {'site_settings': None}
        
        settings_obj = SiteSettings.get_instance()
        return {'site_settings': settings_obj}
    except Exception as e:
        # Return None if anything fails
        return {'site_settings': None}

