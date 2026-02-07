from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Order, OrderItem, Address, PaymentMethod, Blog, ProductMedia, ProductReview
from .forms import ProductReviewForm
from django.db import models
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
from .models import ReturnRequest, HomePage, ContactPage, AuthPage, ProductPageSettings, AgentPageSettings
from . import forms

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


def _get_email_template(template_name):
    """
    Get email template from database.
    Falls back to None if template doesn't exist.
    """
    try:
        from .models import EmailTemplate
        template = EmailTemplate.objects.get(name=template_name, is_active=True)
        return template
    except Exception:
        return None


def _send_email(subject, message, from_email, recipient_list, fail_silently=False, html_message=None):
    """
    Send email using dynamic SMTP configuration from SiteSettings.
    Prioritizes SiteSettings if password is configured, otherwise follows Django settings (DEBUG=Console).
    Auto-detects HTML content if html_message is not provided.
    Supports inline images if 'cid:' reference is found in html_message.
    """
    try:
        import sys
        from .models import SiteSettings
        from django.utils.html import strip_tags
        from django.core.mail import EmailMultiAlternatives
        from email.mime.image import MIMEImage
        
        # Auto-detect HTML if not explicitly provided
        if not html_message and (str(message).strip().startswith('<') or '&gt;' in str(message)):
            # Simple heuristic: if it looks like HTML, treat as HTML
            html_message = message
            message = strip_tags(message) # Fallback plain text
            
        # Check if we have valid SMTP credentials in DB
        site_settings = SiteSettings.get_instance()
        has_db_credentials = bool(site_settings.email_host_password)
        
        connection = None
        if has_db_credentials:
            connection = _get_email_connection()
        elif not (settings.DEBUG or 'test' in sys.argv):
             # Production default behavior
            connection = _get_email_connection()
            
        # Create EmailMultiAlternatives object
        email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=from_email,
            to=recipient_list,
            connection=connection
        )
        
        if html_message:
            email.attach_alternative(html_message, "text/html")
            
            # Check for inline logo requirement
            if 'cid:logo' in html_message and site_settings.logo:
                try:
                    # Attach logo as inline image
                    logo_path = site_settings.logo.path
                    with open(logo_path, 'rb') as f:
                        logo_data = f.read()
                        logo = MIMEImage(logo_data)
                        logo.add_header('Content-ID', '<logo>')
                        logo.add_header('Content-Disposition', 'inline', filename='logo.png')
                        email.attach(logo)
                except Exception as e:
                    logger.error(f"Failed to attach inline logo: {e}")

        email.send(fail_silently=fail_silently)
            
    except Exception as e:
        error_msg = f"Email send failed: {str(e)}"
        logger.error(error_msg)
        if not fail_silently:
            raise


def product_list(request):
    from django.db.models import Q
    
    # Get filter parameters
    search = request.GET.get('search', '')
    sort_price = request.GET.get('sort_price', '')
    agent_id = request.GET.get('agent', '')
    category_slug = request.GET.get('category', '')
    
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
        products = products.filter(supplier_id=agent_id)
    
    # Apply category filter
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
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
    category_slug = request.GET.get('category', '')
    
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
        products = products.filter(supplier_id=agent_id)
    
    # Apply category filter
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
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

    # Get Hero Carousel products (Random 5)
    hero_products = Product.objects.filter(stock__gt=0).order_by('?')[:5]
    
    return render(request, 'store/home.html', {
        'current_page': HomePage.load(),
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
        phone = request.POST.get('phone', '')
        
        # Send email to admin
        if email and message:
            try:
                # Get admin email - send to admin@bhrikutimandap.com
                admin_email = 'admin@bhrikutimandap.com'
                
                # Get from_email to ensure SMTP validation passes
                try:
                    from_email = _get_from_email()
                except Exception:
                    from_email = settings.DEFAULT_FROM_EMAIL
                
                logger.debug(f'Contact form: from_email={from_email}, admin_email={admin_email}, user_email={email}')
                
                # Send to ADMIN
                email_template = _get_email_template('contact_admin')
                if email_template:
                    try:
                        subject = email_template.subject.format(subject_input=subject_input)
                        contact_form_body = email_template.render(
                            name=name,
                            email=email,
                            phone=phone if phone else 'Not provided',
                            subject_input=subject_input,
                            message=message
                        )
                        logger.debug(f'Using contact_admin template: subject={subject}')
                    except Exception as template_error:
                        logger.warning(f'contact_admin template rendering failed: {template_error}. Using fallback.')
                        subject = f'Contact Form: {subject_input}'
                        contact_form_body = f"""New Contact Form Submission

Name: {name}
Email: {email}
Phone: {phone if phone else 'Not provided'}
Subject: {subject_input}

Message:
{message}"""
                else:
                    logger.warning('contact_admin template not found. Using fallback.')
                    subject = f'Contact Form: {subject_input}'
                    contact_form_body = f"""New Contact Form Submission

Name: {name}
Email: {email}
Phone: {phone if phone else 'Not provided'}
Subject: {subject_input}

Message:
{message}"""
                
                logger.debug(f'Sending admin email to {admin_email}')
                _send_email(
                    subject,
                    contact_form_body,
                    from_email,
                    [admin_email],
                    fail_silently=False,  # Will raise exception if fails
                )
                logger.info('Admin notification email sent successfully')
                
                # Send CONFIRMATION to USER
                from datetime import datetime
                confirmation_email_template = _get_email_template('contact_confirmation')
                if confirmation_email_template:
                    try:
                        confirmation_subject = confirmation_email_template.subject
                        confirmation_body = confirmation_email_template.render(
                            name=name,
                            subject_input=subject_input,
                            date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        )
                        logger.debug(f'Using contact_confirmation template: subject={confirmation_subject}')
                    except Exception as template_error:
                        logger.warning(f'contact_confirmation template rendering failed: {template_error}. Using fallback.')
                        confirmation_subject = 'We received your message'
                        confirmation_body = f"""Hello {name},

Thank you for contacting Bhrikutimandap!

We have received your email and appreciate you reaching out to us. Our team will review your message and get back to you shortly.

Your Message Details:
Subject: {subject_input}

We typically respond within 24-48 hours.

Best regards,
Bhrikutimandap Team"""
                else:
                    logger.warning('contact_confirmation template not found. Using fallback.')
                    confirmation_subject = 'We received your message'
                    confirmation_body = f"""Hello {name},

Thank you for contacting Bhrikutimandap!

We have received your email and appreciate you reaching out to us. Our team will review your message and get back to you shortly.

Your Message Details:
Subject: {subject_input}

We typically respond within 24-48 hours.

Best regards,
Bhrikutimandap Team"""
                
                logger.debug(f'Sending confirmation email to {email}')
                _send_email(
                    confirmation_subject,
                    confirmation_body,
                    from_email,
                    [email],
                    fail_silently=False,  # Will raise exception if fails
                )
                logger.info('User confirmation email sent successfully')
                
                messages.success(request, 'Thanks for contacting us. We will reply soon.')
            except Exception as e:
                error_msg = str(e)
                logger.exception(f'Contact form processing failed: {error_msg}')
                # User-friendly error message but log the actual error
                print(f'CONTACT FORM ERROR: {error_msg}')
                messages.error(request, 'Failed to send message. Please try again later.')
        else:
            messages.error(request, 'Please fill in all required fields.')
        return redirect('store:contact')
    return render(request, 'store/contact.html', {'current_page': ContactPage.load()})


# Custom Password Reset View with Email Template Support
from django.contrib.auth.views import PasswordResetView as DjangoPasswordResetView
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

class CustomPasswordResetView(DjangoPasswordResetView):
    """Custom password reset view that uses email templates from database"""
    form_class = forms.CustomPasswordResetForm
    
    def form_valid(self, form):
        """Override form_valid to send custom emails"""
        try:
            email = form.cleaned_data["email"]
            UserModel = form.get_users(email)
            
            for user in UserModel:
                try:
                    # Generate token and uid
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = default_token_generator.make_token(user)
                    reset_link = self.request.build_absolute_uri(
                        f'/accounts/password-reset/{uid}/{token}/'
                    )
                    
                    # Get email template
                    email_template = _get_email_template('password_reset')
                    if email_template:
                        try:
                            template_subject = email_template.render_subject(
                                username=user.username,
                                email=user.email,
                                reset_link=reset_link
                            )
                            template_body = email_template.render(
                                username=user.username,
                                email=user.email,
                                reset_link=reset_link
                            )
                        except Exception as render_error:
                            logger.warning(f'Password reset template rendering failed: {render_error}. Using default.')
                            template_subject = 'Password Reset Request'
                            template_body = f'''Please visit the following link to reset your password:

{reset_link}

This link will expire in 24 hours.

If you did not request this, please ignore this email.'''
                    else:
                        template_subject = 'Password Reset Request'
                        template_body = f'''Please visit the following link to reset your password:

{reset_link}

This link will expire in 24 hours.

If you did not request this, please ignore this email.'''
                    
                    from_email = _get_from_email()
                    _send_email(
                        template_subject,
                        template_body,
                        from_email,
                        [user.email],
                        fail_silently=True,
                    )
                    messages.success(self.request, f'Password reset email sent to {user.email}')
                except Exception as e:
                    logger.exception(f'Error sending password reset email to {user.email}: {e}')
                    messages.error(self.request, 'Failed to send password reset email. Please try again.')
        except Exception as e:
            logger.exception(f'Password reset form processing error: {e}')
            messages.error(self.request, 'An error occurred. Please try again.')
        
        # Return the redirect response (go to done page)
        return super().form_valid(form)


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
    
    # Get all media (images & videos)
    media = product.media.all()
    
    # Get reviews
    reviews = product.reviews.all()
    avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
    full_stars = int(avg_rating)
    half_star = (avg_rating - full_stars) >= 0.5
    empty_stars = 5 - full_stars - (1 if half_star else 0)
    
    review_form = ProductReviewForm()
    
    # Get related products
    related_products = Product.objects.exclude(pk=pk)[:4]
    
    return render(request, 'store/product_detail.html', {
        'product': product,
        'media': media,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'full_stars': range(full_stars),
        'half_star': half_star,
        'empty_stars': range(empty_stars),
        'review_form': review_form,
        'related_products': related_products
    })


@login_required
def add_review(request, product_id):
    """Handle product review submission"""
    product = get_object_or_404(Product, pk=product_id)
    
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            # Check if user already reviewed
            if ProductReview.objects.filter(product=product, user=request.user).exists():
                messages.warning(request, "You have already reviewed this product.")
            else:
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                messages.success(request, "Thank you for your review!")
        else:
            messages.error(request, "Error in review submission. Please try again.")
            
    return redirect('store:product_detail', pk=product_id)


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
            
            if selected_payment_id == 'cod':
                # Handle COD - Get or Create a COD payment method for this user
                selected_payment, created = PaymentMethod.objects.get_or_create(
                    user=request.user,
                    payment_type='cod',
                    defaults={
                        'display_name': 'Cash on Delivery',
                        'token': 'COD',
                        'is_default': False
                    }
                )
            else:
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
    return render(request, 'store/login.html', {'current_page': AuthPage.load()})


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
                return render(request, 'store/register.html', {'current_page': AuthPage.load()})

            # Create inactive user and send activation email with extra fields
            user = User.objects.create_user(
                username=username, 
                password=password, 
                email=email, 
                role=role, 
                is_active=False,
                phone=phone or None,
                company=company or None,
                address_line1=address_line1 or None,
                address_line2=address_line2 or None,
                city=city or None,
                postal_code=postal_code or None
            )
            # Generate OTP instead of activation link
            import random
            otp = str(random.randint(100000, 999999))
            user.otp = otp
            user.otp_expiry = timezone.now() + timezone.timedelta(minutes=10)
            user.save()

            # Store user ID in session for OTP verification
            request.session['registration_user_id'] = user.id

            # Send OTP email using dynamic template
            try:
                # Try to get the OTP template
                otp_template = _get_email_template('otp_verification')
                
                from_email = _get_from_email()
                
                if otp_template:
                    try:
                        subject = otp_template.render_subject(username=username)
                        otp_email_body = otp_template.render(
                            username=username,
                            otp=otp,
                            # logo_url and site_title are auto-injected by render()
                        )
                    except Exception as e:
                        logger.warning(f"OTP template rendering failed: {e}. Using fallback.")
                        subject = 'Your Verification OTP'
                        otp_email_body = f"""Welcome to Bhrikutimandap!

Hello {username},

Your verification OTP is: {otp}

This OTP will expire in 10 minutes.

If you did not create this account, please ignore this email.

Best regards,
Bhrikutimandap Team"""
                else:
                    # Fallback if no template exists
                    subject = 'Your Verification OTP'
                    otp_email_body = f"""Welcome to Bhrikutimandap!

Hello {username},

Your verification OTP is: {otp}

This OTP will expire in 10 minutes.

If you did not create this account, please ignore this email.

Best regards,
Bhrikutimandap Team"""
                
                _send_email(
                    subject,
                    otp_email_body,
                    from_email,
                    [email],
                    fail_silently=False,
                )
                messages.success(request, 'Registered. Please enter the OTP sent to your email to activate your account.')
            except Exception:
                logger.exception('Registration OTP email failed for username=%s', username)
                # Fallback: for testing/dev, if email fails, we might still want to proceed
                print(f"DEBUG: OTP for {username} is {otp}")
                messages.warning(request, f'Account created. For testing, your OTP is {otp}')
            
            return redirect('store:verify_otp')
    return render(request, 'store/register.html', {'current_page': AuthPage.load()})



def verify_otp(request):
    """View to verify registration OTP."""
    user_id = request.session.get('registration_user_id')
    if not user_id:
        messages.error(request, 'Session expired. Please register again.')
        return redirect('store:register')
    
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        otp_input = request.POST.get('otp', '')
        
        if not user.otp or user.otp != otp_input:
            messages.error(request, 'Invalid OTP')
        elif user.otp_expiry < timezone.now():
            messages.error(request, 'OTP has expired. Please register again.')
        else:
            # OTP is valid
            user.is_active = True
            user.otp = None # Clear OTP
            user.save()
            
            # Clear session
            del request.session['registration_user_id']
            
            messages.success(request, 'Account verified! You can now login.')
            return redirect('store:login')
            
    return render(request, 'store/verify_otp.html', {'email': user.email})


def resend_otp(request):
    """View to resend OTP to the user's email."""
    if request.method != 'POST':
        # If accessed via GET, redirect to verify_otp
        # (Though verify_otp might redirect if session missing)
        return redirect('store:verify_otp')
        
    user_id = request.session.get('registration_user_id')
    if not user_id:
        messages.error(request, 'Session expired. Please register again.')
        return redirect('store:register')
        
    try:
        user = User.objects.get(pk=user_id)
        
        # Rate limiting check (optional but good practice)
        # For now, just regenerate and send
        
        # Generate new OTP
        import random
        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.otp_expiry = timezone.now() + timezone.timedelta(minutes=10)
        user.save()
        
        # Send OTP email
        try:
            # Try to get the OTP template
            otp_template = _get_email_template('otp_verification')
            
            from_email = _get_from_email()
            
            if otp_template:
                try:
                    subject = otp_template.render_subject(username=user.username)
                    # Allow dynamic subject override for resend (optional, but good for clarity)
                    if 'Resend' not in subject:
                        subject = f"Resend: {subject}"
                        
                    otp_email_body = otp_template.render(
                        username=user.username,
                        otp=otp,
                        # logo_url and site_title are auto-injected by render()
                    )
                except Exception as e:
                     logger.warning(f"OTP template rendering failed: {e}. Using fallback.")
                     subject = 'Resend: Your Verification OTP'
                     otp_email_body = f"""Welcome to Bhrikutimandap!

Hello {user.username},

Your new verification OTP is: {otp}

This OTP will expire in 10 minutes.

If you did not request this code, please ignore this email.

Best regards,
Bhrikutimandap Team"""
            else:
                subject = 'Resend: Your Verification OTP'
                otp_email_body = f"""Welcome to Bhrikutimandap!

Hello {user.username},

Your new verification OTP is: {otp}

This OTP will expire in 10 minutes.

If you did not request this code, please ignore this email.

Best regards,
Bhrikutimandap Team"""
            
            _send_email(
                subject,
                otp_email_body,
                from_email,
                [user.email],
                fail_silently=False,
            )
            messages.success(request, f'A new OTP has been sent to {user.email}')
        except Exception:
            logger.exception('Resend OTP email failed for username=%s', user.username)
            messages.error(request, 'Failed to send OTP email. Please try again later.')
            
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('store:register')
        
    return redirect('store:verify_otp')


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


@require_http_methods(['POST'])
def api_cart_update(request):
    """
    Update cart item quantity to an exact value.
    If qty <= 0, remove the item.
    """
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

    try:
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            items = CartItem.objects.filter(cart=cart, product=product)
            if items.exists():
                ci = items.first()
                if qty > 0:
                    ci.quantity = qty
                    ci.save()
                else:
                    ci.delete()
                # Clean up duplicates
                if items.count() > 1:
                    items.exclude(pk=ci.pk).delete()
            elif qty > 0:
                CartItem.objects.create(cart=cart, product=product, quantity=qty)
            
            total_count = sum(i.quantity for i in cart.items.all())
        else:
            cart = _get_cart(request)
            if qty > 0:
                cart[str(product_id)] = qty
            else:
                if str(product_id) in cart:
                    del cart[str(product_id)]
            request.session['cart'] = cart
            request.session.modified = True
            total_count = sum(cart.values())

        return JsonResponse({'ok': True, 'cart_count': total_count})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET', 'POST'])
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

    try:
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            # Handle potential multiple objects returned for CartItem
            items = CartItem.objects.filter(cart=cart, product=product)
            if items.exists():
                ci = items.first()
                ci.quantity += qty
                ci.save()
                # Clean up duplicates if any
                if items.count() > 1:
                    items.exclude(pk=ci.pk).delete()
            else:
                CartItem.objects.create(cart=cart, product=product, quantity=qty)
            
            total_count = sum(i.quantity for i in cart.items.all())
        else:
            cart = _get_cart(request)
            cart[str(product_id)] = cart.get(str(product_id), 0) + qty
            request.session['cart'] = cart
            request.session.modified = True
            total_count = sum(cart.values())

        return JsonResponse({'ok': True, 'cart_count': total_count})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)


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
