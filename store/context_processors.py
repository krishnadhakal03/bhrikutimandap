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


def categories(request):
    """Add all categories to context."""
    from .models import Category
    try:
        return {'categories': Category.objects.all()}
    except Exception:
        return {'categories': []}

def dynamic_pages(request):
    """Add dynamic page settings to all template contexts."""
    try:
        from .models import HomePage, ContactPage, AuthPage, ProductPageSettings, AgentPageSettings
        
        # Helper to safely load or create
        def load_safe(model):
            try:
                return model.load()
            except Exception:
                return None

        return {
            'home_page': load_safe(HomePage),
            'contact_page': load_safe(ContactPage),
            'auth_page': load_safe(AuthPage),
            'product_page_settings': load_safe(ProductPageSettings),
            'agent_page_settings': load_safe(AgentPageSettings),
        }
    except Exception:
        return {}


def chat_unread_counts(request):
    """Add unread chat counters for navbar/sidebar badges."""
    if not request.user.is_authenticated:
        return {
            'customer_unread_messages': 0,
            'agent_unread_messages': 0,
            'chat_unread_total': 0,
        }

    from django.db import connection
    from django.db.utils import OperationalError, ProgrammingError
    from .models import SellerMessage

    # If chat tables are not migrated yet, keep templates functional.
    try:
        table_names = connection.introspection.table_names()
        if 'store_sellermessage' not in table_names:
            return {
                'customer_unread_messages': 0,
                'agent_unread_messages': 0,
                'chat_unread_total': 0,
            }
    except Exception:
        return {
            'customer_unread_messages': 0,
            'agent_unread_messages': 0,
            'chat_unread_total': 0,
        }

    try:
        customer_unread = SellerMessage.objects.filter(
            conversation__customer=request.user,
            is_read=False,
        ).exclude(sender=request.user).count()

        agent_unread = 0
        if request.user.role == 'agent':
            agent_unread = SellerMessage.objects.filter(
                conversation__seller=request.user,
                is_read=False,
            ).exclude(sender=request.user).count()
    except (OperationalError, ProgrammingError):
        customer_unread = 0
        agent_unread = 0

    return {
        'customer_unread_messages': customer_unread,
        'agent_unread_messages': agent_unread,
        'chat_unread_total': customer_unread + agent_unread,
    }
