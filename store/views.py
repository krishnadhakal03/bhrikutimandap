from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Order, OrderItem, Address, PaymentMethod, Blog
from django.contrib.auth import get_user_model
from django.http import JsonResponse
import json
from django.utils import timezone

User = get_user_model()
from .models import Cart, CartItem, Product
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, get_connection
from django.conf import settings
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .services import process_order_created, process_return_approval
from .models import ReturnRequest

import logging

logger = logging.getLogger(__name__)


def _get_email_connection():
    """
    Get SMTP connection with settings from SiteSettings or environment variables.
    """
    try:
        from .models import SiteSettings
        site_settings = SiteSettings.get_instance()
        
        return get_connection(
            backend='django.core.mail.backends.smtp.EmailBackend',
            host=site_settings.email_host or settings.EMAIL_HOST,
            port=site_settings.email_port or settings.EMAIL_PORT,
            username=site_settings.email_host_user or settings.EMAIL_HOST_USER,
            password=site_settings.email_host_password or settings.EMAIL_HOST_PASSWORD,
            use_tls=site_settings.email_use_tls,
            fail_silently=False,
        )
    except Exception as e:
        logger.debug(f"Could not get SiteSettings for email connection: {e}. Using default.")
        # Return None to use Django's default settings
        return None


def _get_from_email():
    """
    Get the DEFAULT_FROM_EMAIL from SiteSettings or settings.
    """
    try:
        from .models import SiteSettings
        site_settings = SiteSettings.get_instance()
        return site_settings.default_from_email or settings.DEFAULT_FROM_EMAIL
    except Exception:
        return settings.DEFAULT_FROM_EMAIL


def _send_email(subject, message, from_email, recipient_list, fail_silently=False):
    """
    Send email using dynamic SMTP configuration from SiteSettings.
    In DEBUG/test mode, uses locmem or console backend.
    In production, uses SMTP with dynamic settings from SiteSettings.
    """
    try:
        import sys
        # In DEBUG mode or test mode, use configured test backend (locmem/console)
        if settings.DEBUG or 'test' in sys.argv:
            send_mail(subject, message, from_email, recipient_list, fail_silently=fail_silently)
        else:
            # Get connection with dynamic settings
            connection = _get_email_connection()
            send_mail(
                subject, 
                message, 
                from_email, 
                recipient_list, 
                connection=connection,
                fail_silently=fail_silently
            )
    except Exception as e:
        logger.exception(f"Email send failed: {e}")
        raise


def product_list(request):
    from django.db.models import Q
    
    # Get filter parameters
    search = request.GET.get('search', '')
    sort_price = request.GET.get('sort_price', '')
    agent_id = request.GET.get('agent', '')
    
    # Start with all products that are in stock
    products = Product.objects.filter(stock__gt=0)
    
    # Apply search filter
    if search:
        products = products.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search)
        )
    
    # Apply agent filter
    if agent_id:
        products = products.filter(agent_id=agent_id)
    
    # Apply price sorting
    if sort_price == 'low_to_high':
        products = products.order_by('price')
    elif sort_price == 'high_to_low':
        products = products.order_by('-price')
    
    # Add delivery info to each product instance
    for product in products:
        product.agent_name = product.get_agent_name()
        product.in_stock = product.is_in_stock()
        product.estimated_delivery = product.get_estimated_delivery()
    
    # Get all agents for filter dropdown
    from store.models import AgentProfile
    agents = AgentProfile.objects.filter(approval_status='approved').order_by('company_name')
    
    return render(request, 'store/product_list.html', {
        'products': products,
        'agents': agents,
        'search': search,
        'sort_price': sort_price,
        'agent_id': agent_id
    })


def home(request):
    from django.db.models import Q
    
    # Get filter parameters
    search = request.GET.get('search', '')
    sort_price = request.GET.get('sort_price', '')
    agent_id = request.GET.get('agent', '')
    
    # Start with all products that are in stock
    products = Product.objects.filter(stock__gt=0)
    
    # Apply search filter
    if search:
        products = products.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search)
        )
    
    # Apply agent filter
    if agent_id:
        products = products.filter(agent_id=agent_id)
    
    # Apply price sorting
    if sort_price == 'low_to_high':
        products = products.order_by('price')
    elif sort_price == 'high_to_low':
        products = products.order_by('-price')
    else:
        # Default: show latest products
        products = products.order_by('-id')
    
    # Limit to 12 for display
    products_list = products[:12]
    
    # Add agent info to products
    for product in products_list:
        product.agent_name = product.get_agent_name()
    
    # Get all agents for filter dropdown
    from store.models import AgentProfile
    agents = AgentProfile.objects.filter(approval_status='approved').order_by('company_name')
    
    # Get best sellers (top 8 products)
    best_sellers = Product.objects.filter(stock__gt=0).order_by('-id')[:8]
    
    return render(request, 'store/home.html', {
        'products': products_list,
        'best_sellers': best_sellers,
        'agents': agents,
        'search': search,
        'sort_price': sort_price,
        'agent_id': agent_id
    })


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', 'Not provided')
        email = request.POST.get('email', '')
        subject_input = request.POST.get('subject', 'Contact Form Inquiry')
        message = request.POST.get('message', '')
        
        # Send email to admin
        if email and message:
            try:
                # Get contact email from SiteSettings or use default
                try:
                    from .models import SiteSettings
                    site_settings = SiteSettings.get_instance()
                    contact_email = site_settings.contact_email or settings.CONTACT_EMAIL
                except Exception:
                    contact_email = settings.CONTACT_EMAIL
                
                _send_email(
                    f'Contact Form: {subject_input}',
                    f'From: {name} ({email})\n\nMessage:\n{message}',
                    email,
                    [contact_email],
                    fail_silently=False,
                )
                messages.success(request, 'Thanks for contacting us. We will reply soon.')
            except Exception as e:
                logger.exception('Contact form email failed')
                messages.error(request, 'Failed to send message. Please try again later.')
        else:
            messages.error(request, 'Please fill in all required fields.')
        return redirect('store:contact')
    return render(request, 'store/contact.html')


def blog_view(request):
    """Display list of published blog posts"""
    blogs = Blog.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'store/blog.html', {'blogs': blogs})


def blog_detail_view(request, slug):
    """Display a single blog post"""
    blog = get_object_or_404(Blog, slug=slug, is_published=True)
    # Get related blogs (same category or recent)
    related_blogs = Blog.objects.filter(is_published=True).exclude(pk=blog.pk)[:3]
    return render(request, 'store/blog_detail.html', {
        'blog': blog,
        'related_blogs': related_blogs
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Get related products
    related_products = Product.objects.exclude(pk=pk)[:4]
    
    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related_products
    })


def _get_cart(request):
    return request.session.setdefault('cart', {})


def add_to_cart(request, product_id):
    cart = _get_cart(request)
    qty = int(request.GET.get('qty', 1))
    cart[str(product_id)] = cart.get(str(product_id), 0) + qty
    request.session.modified = True
    messages.success(request, 'Added to cart')
    return redirect('store:product_list')


def _merge_session_cart_into_user(request, user):
    session_cart = request.session.get('cart', {})
    if not session_cart:
        return
    # Ensure user has a Cart
    cart, _ = Cart.objects.get_or_create(user=user)
    for pid, qty in session_cart.items():
        product = None
        try:
            from .models import Product, CartItem
            product = Product.objects.get(pk=int(pid))
        except Exception:
            continue
        ci, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            ci.quantity += qty
        else:
            ci.quantity = qty
        ci.save()
    # Clear session cart
    request.session['cart'] = {}
    request.session.modified = True


def cart_view(request):
    items = []
    total = 0
    
    if request.user.is_authenticated:
        try:
            cart = request.user.cart
            for item in cart.items.all():
                line_total = item.product.price * item.quantity
                total += line_total
                items.append({
                    'product': item.product,
                    'quantity': item.quantity,
                    'line_total': line_total
                })
        except Cart.DoesNotExist:
            pass
    else:
        cart = _get_cart(request)
        for pid, qty in cart.items():
            try:
                product = Product.objects.get(pk=int(pid))
            except Product.DoesNotExist:
                continue
            line_total = product.price * qty
            total += line_total
            items.append({'product': product, 'quantity': qty, 'line_total': line_total})
    
    return render(request, 'store/cart.html', {'items': items, 'total': total})


@login_required
def checkout(request):
    """Checkout flow: display payment methods and delivery address, then create order."""
    
    # Get cart items - for authenticated users from database, for anonymous from session
    cart_items_to_process = []
    insufficient_stock = []
    
    if request.user.is_authenticated:
        # For authenticated users, get from database cart
        try:
            cart = request.user.cart
            for item in cart.items.all():
                if item.product.stock < item.quantity:
                    insufficient_stock.append(f'"{item.product.title}" has only {item.product.stock} units available (you requested {item.quantity})')
                else:
                    cart_items_to_process.append((item.product, item.quantity))
        except Cart.DoesNotExist:
            messages.info(request, 'Your cart is empty')
            return redirect('store:product_list')
    else:
        # For anonymous users, get from session
        session_cart = _get_cart(request)
        if not session_cart:
            messages.info(request, 'Your cart is empty')
            return redirect('store:product_list')
        
        for pid, qty in session_cart.items():
            try:
                product = Product.objects.get(pk=int(pid))
            except Product.DoesNotExist:
                insufficient_stock.append(f"Product {pid} not found")
                continue
            
            if product.stock < qty:
                insufficient_stock.append(f'"{product.title}" has only {product.stock} units available (you requested {qty})')
            else:
                cart_items_to_process.append((product, qty))
    
    # Check if we have items to process
    if not cart_items_to_process:
        if insufficient_stock:
            for msg in insufficient_stock:
                messages.error(request, msg)
        else:
            messages.error(request, 'No valid items in cart')
        return redirect('store:cart')
    
    # Display checkout form for GET request or first visit
    if request.method == 'GET':
        # Get user's addresses and payment methods
        addresses = request.user.addresses.all() if request.user.is_authenticated else []
        payment_methods = request.user.payment_methods.filter(is_active=True) if request.user.is_authenticated else []
        
        # Prepare cart items with subtotals
        cart_items_display = []
        for product, qty in cart_items_to_process:
            cart_items_display.append({
                'product': product,
                'quantity': qty,
                'subtotal': product.price * qty
            })
        
        # Calculate cart total
        cart_total = sum(item['subtotal'] for item in cart_items_display)
        
        context = {
            'cart_items': cart_items_display,
            'cart_total': cart_total,
            'addresses': addresses,
            'payment_methods': payment_methods,
            'insufficient_stock': insufficient_stock,
        }
        return render(request, 'store/checkout.html', context)
    
    # Process checkout on POST
    elif request.method == 'POST':
        selected_address_id = request.POST.get('delivery_address')
        selected_payment_id = request.POST.get('payment_method')
        
        # Validate selections
        if not selected_address_id and request.user.is_authenticated:
            messages.error(request, 'Please select a delivery address')
            return redirect('store:checkout')
        
        if not selected_payment_id and request.user.is_authenticated:
            messages.error(request, 'Please select a payment method')
            return redirect('store:checkout')
        
        # Get selected address and payment method
        selected_address = None
        selected_payment = None
        
        if request.user.is_authenticated:
            try:
                selected_address = Address.objects.get(pk=selected_address_id, user=request.user)
            except Address.DoesNotExist:
                messages.error(request, 'Invalid address selected')
                return redirect('store:checkout')
            
            try:
                selected_payment = PaymentMethod.objects.get(pk=selected_payment_id, user=request.user)
            except PaymentMethod.DoesNotExist:
                messages.error(request, 'Invalid payment method selected')
                return redirect('store:checkout')
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            delivery_address=selected_address,
            payment_method=selected_payment if request.user.is_authenticated else None
        )
        
        # Create order items
        for product, qty in cart_items_to_process:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty
            )
        
        # Process order: deduct stock and create delivery records
        if process_order_created(order):
            # Clear cart (both session and user cart if exists)
            request.session['cart'] = {}
            request.session.modified = True
            if request.user.is_authenticated:
                try:
                    cart_obj = request.user.cart
                    cart_obj.items.all().delete()
                except Cart.DoesNotExist:
                    pass
            
            messages.success(request, f'Order #{order.id} placed successfully! You will receive an email confirmation.')
            return redirect('store:order_detail', order_id=order.id)
        else:
            messages.error(request, 'Error processing order. Please try again.')
            order.delete()
            return redirect('store:checkout')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            # Merge session cart
            _merge_session_cart_into_user(request, user)
            login(request, user)
            # Redirect based on user role
            if user.role == 'agent':
                # Agent user - redirect to agent dashboard
                return redirect('agent:dashboard')
            else:
                # Customer user - redirect to customer portal
                return redirect('store:product_list')
        messages.error(request, 'Invalid credentials')
    return render(request, 'store/login.html')


def logout_view(request):
    logout(request)
    return redirect('store:product_list')


def register_view(request):
    # Simple registration with role selection; default role = customer
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email', '')
        role = request.POST.get('role', 'customer')
        # additional fields
        phone = request.POST.get('phone', '')
        company = request.POST.get('company', '')
        address_line1 = request.POST.get('address_line1', '')
        address_line2 = request.POST.get('address_line2', '')
        city = request.POST.get('city', '')
        postal_code = request.POST.get('postal_code', '')

        if not username or not password:
            messages.error(request, 'Username and password required')
        elif not email:
            messages.error(request, 'Email address is required')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
        else:
            # Prevent elevation to admin role via registration form
            if role not in ('customer', 'agent'):
                role = 'customer'
            # Validate password via Django validators
            from django.contrib.auth.password_validation import validate_password
            from django.core.exceptions import ValidationError
            try:
                validate_password(password)
            except ValidationError as e:
                messages.error(request, '; '.join(e.messages))
                return render(request, 'store/register.html')

            # Create inactive user and send activation email
            user = User.objects.create_user(username=username, password=password, email=email, role=role, is_active=False)
            # store extra profile fields
            user.phone = phone or None
            user.company = company or None
            user.address_line1 = address_line1 or None
            user.address_line2 = address_line2 or None
            user.city = city or None
            user.postal_code = postal_code or None
            user.save()
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_path = reverse('store:activate', kwargs={'uidb64': uid, 'token': token})
            activation_link = request.build_absolute_uri(activation_path)

            # Send activation email. In production, missing/incorrect SMTP settings should not 500 the request.
            try:
                from_email = _get_from_email()
                _send_email(
                    'Activate your account',
                    f'Activate at: {activation_link}',
                    from_email,
                    [email],
                    fail_silently=False,
                )
                messages.success(request, 'Registered. Please check your email to activate your account.')
            except Exception:
                logger.exception('Registration email failed for username=%s', username)
                # Fallback: activate immediately so registration still works.
                user.is_active = True
                user.save(update_fields=['is_active'])
                if getattr(settings, 'DEBUG', False):
                    messages.warning(request, f'Email send failed (dev). Activation link: {activation_link}')
                else:
                    messages.warning(request, 'Account created, but we could not send the activation email. You can login now.')
            return redirect('store:product_list')
    return render(request, 'store/register.html')


def activate_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None
    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Account activated. You can login now.')
        return redirect('store:login')
    messages.error(request, 'Activation link invalid')
    return redirect('store:product_list')


@require_http_methods(['GET', 'POST'])
def contact_view(request):
    """Simple contact page: shows a form and on POST sends a console email (dev)."""
    sent = False
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        message = request.POST.get('message', '')
        subject = f'Contact form from {name or email}'
        body = f'From: {name} <{email}>\n\n{message}'
        try:
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL])
            messages.success(request, 'Thanks — your message was sent (dev).')
            sent = True
        except Exception:
            messages.error(request, 'Failed to send message (dev).')
    return render(request, 'store/contact.html', {'sent': sent})


def blog_view(request):
    """Simple blog list — use Product entries as demo blog cards for the prototype."""
    posts = Product.objects.all().order_by('-created_at')[:12]
    # Map products to lightweight post-like dicts for template
    posts_data = []
    for p in posts:
        posts_data.append({
            'title': p.title,
            'excerpt': (p.description[:140] + '...') if p.description else '',
            'image': p.image.url if p.image else None,
            'url': '#',
        })
    return render(request, 'store/blog.html', {'posts': posts_data})


def api_cart_add(request):
    # Expects POST with product_id and qty (int)
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    try:
        data = json.loads(request.body.decode())
        product_id = int(data.get('product_id'))
        qty = int(data.get('qty', 1))
    except Exception:
        return JsonResponse({'error': 'Invalid data'}, status=400)

    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        ci, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            ci.quantity += qty
        else:
            ci.quantity = qty
        ci.save()
        total_count = sum(i.quantity for i in cart.items.all())
    else:
        cart = _get_cart(request)
        cart[str(product_id)] = cart.get(str(product_id), 0) + qty
        request.session['cart'] = cart
        request.session.modified = True
        total_count = sum(cart.values())

    return JsonResponse({'ok': True, 'cart_count': total_count})


def api_cart_remove(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    try:
        data = json.loads(request.body.decode())
        product_id = int(data.get('product_id'))
    except Exception:
        return JsonResponse({'error': 'Invalid data'}, status=400)
    if request.user.is_authenticated:
        try:
            cart = request.user.cart
        except Cart.DoesNotExist:
            return JsonResponse({'ok': True, 'cart_count': 0})
        CartItem.objects.filter(cart=cart, product_id=product_id).delete()
        total_count = sum(i.quantity for i in cart.items.all())
    else:
        cart = _get_cart(request)
        cart.pop(str(product_id), None)
        request.session['cart'] = cart
        request.session.modified = True
        total_count = sum(cart.values())
    return JsonResponse({'ok': True, 'cart_count': total_count})


def api_cart_detail(request):
    items = []
    total = 0
    if request.user.is_authenticated:
        try:
            cart = request.user.cart
            for it in cart.items.all():
                items.append({'product_id': it.product_id, 'title': it.product.title, 'quantity': it.quantity, 'line_total': float(it.total_price())})
                total += float(it.total_price())
        except Cart.DoesNotExist:
            pass
    else:
        cart = _get_cart(request)
        for pid, qty in cart.items():
            try:
                p = Product.objects.get(pk=int(pid))
            except Product.DoesNotExist:
                continue
            items.append({'product_id': int(pid), 'title': p.title, 'quantity': qty, 'line_total': float(p.price * qty)})
            total += float(p.price * qty)
    return JsonResponse({'items': items, 'total': total})


# ============ AGENT DASHBOARD VIEWS ============

def agent_required(view_func):
    """Decorator to ensure user is logged in and is an agent."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login first')
            return redirect('store:login')
        if request.user.role != 'agent':
            messages.error(request, 'Only agents can access this')
            return redirect('store:product_list')
        return view_func(request, *args, **kwargs)
    return wrapper


@agent_required
def agent_dashboard(request):
    """List all products belonging to the agent."""
    products = Product.objects.filter(supplier=request.user)
    return render(request, 'store/agent_dashboard.html', {'products': products})


@agent_required
def agent_add_product(request):
    """Add a new product by the agent."""
    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        price = request.POST.get('price', 0)
        stock = request.POST.get('stock', 0)
        expiration_date = request.POST.get('expiration_date', None)
        delivery_rules = request.POST.get('delivery_rules', '')
        payment_methods = request.POST.get('payment_methods', '')
        image = request.FILES.get('image', None)

        if not title or not price:
            messages.error(request, 'Title and price are required')
            return render(request, 'store/agent_product_form.html')

        try:
            price = float(price)
            stock = int(stock) if stock else 0
        except (ValueError, TypeError):
            messages.error(request, 'Invalid price or stock format')
            return render(request, 'store/agent_product_form.html')

        product = Product.objects.create(
            title=title,
            description=description,
            price=price,
            stock=stock,
            supplier=request.user,
            expiration_date=expiration_date or None,
            delivery_rules=delivery_rules,
            payment_methods=payment_methods,
            image=image
        )
        messages.success(request, f'Product "{title}" created successfully!')
        return redirect('store:agent_dashboard')

    return render(request, 'store/agent_product_form.html', {'action': 'Add'})


@agent_required
def agent_edit_product(request, product_id):
    """Edit a product belonging to the agent."""
    product = get_object_or_404(Product, pk=product_id, supplier=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        price = request.POST.get('price', product.price)
        stock = request.POST.get('stock', product.stock)
        expiration_date = request.POST.get('expiration_date', product.expiration_date)
        delivery_rules = request.POST.get('delivery_rules', '')
        payment_methods = request.POST.get('payment_methods', '')
        image = request.FILES.get('image', None)

        if not title or not price:
            messages.error(request, 'Title and price are required')
            return render(request, 'store/agent_product_form.html', {'product': product, 'action': 'Edit'})

        try:
            price = float(price)
            stock = int(stock) if stock else 0
        except (ValueError, TypeError):
            messages.error(request, 'Invalid price or stock format')
            return render(request, 'store/agent_product_form.html', {'product': product, 'action': 'Edit'})

        product.title = title
        product.description = description
        product.price = price
        product.stock = stock
        product.expiration_date = expiration_date or None
        product.delivery_rules = delivery_rules
        product.payment_methods = payment_methods
        if image:
            product.image = image
        product.save()
        messages.success(request, f'Product "{title}" updated successfully!')
        return redirect('store:agent_dashboard')

    return render(request, 'store/agent_product_form.html', {'product': product, 'action': 'Edit'})


@agent_required
def agent_delete_product(request, product_id):
    """Delete a product belonging to the agent."""
    product = get_object_or_404(Product, pk=product_id, supplier=request.user)
    
    if request.method == 'POST':
        product_title = product.title
        product.delete()
        messages.success(request, f'Product "{product_title}" deleted successfully!')
        return redirect('store:agent_dashboard')

    return render(request, 'store/agent_product_confirm_delete.html', {'product': product})


# ============ ORDER MANAGEMENT VIEWS ============

@login_required
def order_detail(request, order_id):
    """View details of a specific order."""
    order = get_object_or_404(Order, pk=order_id)
    
    # Only allow customer or supplier to view order details
    if request.user != order.user and not order.items.filter(product__supplier=request.user).exists():
        messages.error(request, 'You do not have permission to view this order')
        return redirect('store:product_list')
    
    order_items = order.items.all()
    total = sum(item.total_price() for item in order_items)
    
    context = {
        'order': order,
        'items': order_items,
        'total': total,
    }
    return render(request, 'store/order_detail.html', context)


@login_required
def request_return(request, order_item_id):
    """Customer requests return for a specific order item."""
    order_item = get_object_or_404(OrderItem, pk=order_item_id)
    
    # Only the customer who purchased can request return
    if request.user != order_item.order.user:
        messages.error(request, 'You do not have permission to request return for this item')
        return redirect('store:product_list')
    
    # Check if return already exists
    if hasattr(order_item, 'return_request'):
        if order_item.return_request.status != 'rejected':
            messages.error(request, 'Return already requested or processed for this item')
            return redirect('store:order_detail', order_id=order_item.order.id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        description = request.POST.get('description', '')
        
        if not reason:
            messages.error(request, 'Please select a reason for return')
            return render(request, 'store/request_return.html', {'order_item': order_item})
        
        if not description:
            messages.error(request, 'Please provide details about the return')
            return render(request, 'store/request_return.html', {'order_item': order_item})
        
        # Create return request
        ReturnRequest.objects.create(
            order_item=order_item,
            return_reason=reason,
            return_description=description,
            status='requested'
        )
        
        messages.success(request, 'Return request submitted. Agent will review and approve/deny shortly.')
        return redirect('store:order_detail', order_id=order_item.order.id)
    
    return render(request, 'store/request_return.html', {'order_item': order_item})


@login_required
def toggle_role(request):
    """Toggle user role between 'customer' and 'agent'. Prevent elevation to admin.
    This is a convenience endpoint for prototype only."""
    user = request.user
    # Only allow toggling between customer and agent
    if user.role == 'agent':
        user.role = 'customer'
        user.save()
        messages.success(request, 'Switched to Customer view')
    else:
        user.role = 'agent'
        user.save()
        messages.success(request, 'Switched to Agent view')
    # redirect back to referring page when possible
    next_url = request.META.get('HTTP_REFERER') or '/' 
    return redirect(next_url)


# ============= Customer Profile Management Views =============

@login_required
def customer_dashboard(request):
    """Customer dashboard showing overview of profile, orders, and wishlist"""
    user = request.user
    recent_orders = user.orders.all()[:5]
    wishlist = user.wishlist if hasattr(user, 'wishlist') else None
    addresses = user.addresses.all()
    payment_methods = user.payment_methods.all()
    
    context = {
        'recent_orders': recent_orders,
        'wishlist': wishlist,
        'addresses': addresses,
        'payment_methods': payment_methods,
        'total_orders': user.orders.count(),
        'total_addresses': user.addresses.count(),
        'total_payment_methods': user.payment_methods.filter(is_active=True).count(),
    }
    return render(request, 'store/customer_dashboard.html', context)


@login_required
def profile_detail(request):
    """View and edit user profile"""
    from .forms import UserProfileForm
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('store:customer_dashboard')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'user': request.user
    }
    return render(request, 'store/profile_detail.html', context)


@login_required
def address_list(request):
    """List all addresses for the user"""
    addresses = request.user.addresses.all()
    context = {'addresses': addresses}
    return render(request, 'store/address_list.html', context)


@login_required
def address_create(request):
    """Create a new delivery address"""
    from .forms import AddressForm
    
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            
            # If this is marked as default, remove default from others
            if address.is_default:
                request.user.addresses.all().update(is_default=False)
            
            address.save()
            messages.success(request, 'Address added successfully!')
            return redirect('store:address_list')
    else:
        form = AddressForm()
    
    context = {'form': form, 'action': 'Add'}
    return render(request, 'store/address_form.html', context)


@login_required
def address_update(request, address_id):
    """Update an existing address"""
    from .forms import AddressForm
    
    address = get_object_or_404(Address, pk=address_id, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            address = form.save(commit=False)
            
            # If this is marked as default, remove default from others
            if address.is_default:
                request.user.addresses.exclude(pk=address.pk).update(is_default=False)
            
            address.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('store:address_list')
    else:
        form = AddressForm(instance=address)
    
    context = {'form': form, 'action': 'Edit', 'address': address}
    return render(request, 'store/address_form.html', context)


@login_required
def address_delete(request, address_id):
    """Delete an address"""
    address = get_object_or_404(Address, pk=address_id, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully!')
        return redirect('store:address_list')
    
    context = {'address': address}
    return render(request, 'store/address_confirm_delete.html', context)


@login_required
def address_set_default(request, address_id):
    """Set an address as default"""
    address = get_object_or_404(Address, pk=address_id, user=request.user)
    
    # Remove default from all other addresses
    request.user.addresses.all().update(is_default=False)
    
    # Set this as default
    address.is_default = True
    address.save()
    
    messages.success(request, 'Default address updated!')
    return redirect('store:address_list')


@login_required
def payment_method_list(request):
    """List all payment methods for the user"""
    payment_methods = request.user.payment_methods.filter(is_active=True)
    context = {'payment_methods': payment_methods}
    return render(request, 'store/payment_method_list.html', context)


@login_required
def payment_method_create(request):
    """Create a new payment method (token only, no raw card data)"""
    from .forms import PaymentMethodForm
    
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            payment_method = form.save(commit=False)
            payment_method.user = request.user
            
            # Generate a mock token (in production, use payment gateway)
            import uuid
            payment_method.token = f"token_{uuid.uuid4().hex[:20]}"
            
            # If this is marked as default, remove default from others
            if payment_method.is_default:
                request.user.payment_methods.update(is_default=False)
            
            payment_method.save()
            messages.success(request, 'Payment method added successfully!')
            return redirect('store:payment_method_list')
    else:
        form = PaymentMethodForm()
    
    context = {'form': form, 'action': 'Add'}
    return render(request, 'store/payment_method_form.html', context)


@login_required
def payment_method_delete(request, method_id):
    """Delete a payment method (soft delete by marking inactive)"""
    payment_method = get_object_or_404(PaymentMethod, pk=method_id, user=request.user)
    
    if request.method == 'POST':
        payment_method.is_active = False
        payment_method.save()
        messages.success(request, 'Payment method removed!')
        return redirect('store:payment_method_list')
    
    context = {'payment_method': payment_method}
    return render(request, 'store/payment_method_confirm_delete.html', context)


@login_required
def payment_method_set_default(request, method_id):
    """Set a payment method as default"""
    payment_method = get_object_or_404(PaymentMethod, pk=method_id, user=request.user)
    
    # Remove default from all other methods
    request.user.payment_methods.update(is_default=False)
    
    # Set this as default
    payment_method.is_default = True
    payment_method.save()
    
    messages.success(request, 'Default payment method updated!')
    return redirect('store:payment_method_list')


@login_required
def order_history(request):
    """View order history with filtering and pagination"""
    from .forms import OrderFilterForm
    from datetime import timedelta
    
    orders = request.user.orders.all().order_by('-created_at')
    
    # Apply filters
    form = OrderFilterForm(request.GET or None)
    if form.is_valid():
        status = form.cleaned_data.get('status')
        date_range = form.cleaned_data.get('date_range')
        search = form.cleaned_data.get('search')
        
        if status:
            orders = orders.filter(status=status)
        
        if date_range:
            today = timezone.now()
            if date_range == '30days':
                start_date = today - timedelta(days=30)
            elif date_range == '90days':
                start_date = today - timedelta(days=90)
            elif date_range == '6months':
                start_date = today - timedelta(days=180)
            elif date_range == '1year':
                start_date = today - timedelta(days=365)
            else:
                start_date = None
            
            if start_date:
                orders = orders.filter(created_at__gte=start_date)
        
        if search:
            orders = orders.filter(id=search)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(orders, 10)  # 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'orders': page_obj.object_list,
        'form': form,
    }
    return render(request, 'store/order_history.html', context)


@login_required
def wishlist_view(request):
    """View user's wishlist"""
    from .models import Wishlist
    
    # Get or create wishlist
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    items = wishlist.items.all()
    
    context = {
        'wishlist': wishlist,
        'items': items,
        'total_items': items.count(),
    }
    return render(request, 'store/wishlist.html', context)


@login_required
def wishlist_add(request, product_id):
    """Add product to wishlist"""
    from .models import Wishlist, WishlistItem
    
    product = get_object_or_404(Product, pk=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    # Check if product already in wishlist
    if wishlist.items.filter(product=product).exists():
        return JsonResponse({'ok': False, 'message': 'Product already in wishlist'})
    
    WishlistItem.objects.create(wishlist=wishlist, product=product)
    
    return JsonResponse({
        'ok': True,
        'message': 'Added to wishlist',
        'wishlist_count': wishlist.items.count()
    })


@login_required
def wishlist_remove(request, product_id):
    """Remove product from wishlist"""
    from .models import Wishlist
    
    product = get_object_or_404(Product, pk=product_id)
    wishlist = get_object_or_404(Wishlist, user=request.user)
    
    wishlist.items.filter(product=product).delete()
    
    return JsonResponse({
        'ok': True,
        'message': 'Removed from wishlist',
        'wishlist_count': wishlist.items.count()
    })
