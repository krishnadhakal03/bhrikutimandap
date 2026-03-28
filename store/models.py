from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import base64
import hashlib
import json

from cryptography.fernet import Fernet, InvalidToken


class User(AbstractUser):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('agent', 'Agent'),
        ('admin', 'Administrator'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    # Additional real-ecommerce fields
    phone = models.CharField(max_length=30, blank=True, null=True)
    company = models.CharField(max_length=200, blank=True, null=True)
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    verified = models.BooleanField(default=False)  # for agents/suppliers
    approved_by_admin = models.BooleanField(default=False)  # only for agents
    
    # OTP fields
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    supplier = models.ForeignKey(User, limit_choices_to={'role': 'agent'}, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    expiration_date = models.DateTimeField(null=True, blank=True, help_text="Product expiration date if applicable")
    delivery_rules = models.TextField(blank=True, help_text="Delivery terms, e.g., 'Free shipping', 'Ships in 2-3 days'")
    payment_methods = models.CharField(max_length=200, blank=True, help_text="Comma-separated: COD, Card, UPI")
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.supplier.username}"

    def is_in_stock(self):
        return self.stock > 0

    def is_expired(self):
        if self.expiration_date:
            return timezone.now() > self.expiration_date
        return False
    
    def get_estimated_delivery(self):
        """Get estimated delivery time from agent"""
        if self.supplier and hasattr(self.supplier, 'agent_profile'):
            # Check if agent has delivery partners
            delivery_partners = DeliveryPartner.objects.filter(status='active')
            if delivery_partners.exists():
                avg_hours = delivery_partners.aggregate(models.Avg('avg_delivery_time_hours'))['avg_delivery_time_hours__avg']
                if avg_hours:
                    return timezone.now() + timedelta(hours=int(avg_hours))
        return timezone.now() + timedelta(hours=24)  # Default 24 hours
    
    def get_agent_name(self):
        """Get agent/supplier name"""
        return self.supplier.get_full_name() or self.supplier.username if self.supplier else "Unknown"


class ProductMedia(models.Model):
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='product_media/')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, default='image')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_media_type_display()} for {self.product.title}"


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review for {self.product.title} by {self.user.username}"


class SellerConversation(models.Model):
    """Direct in-app chat thread between one customer and one seller for a product."""
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller_conversations')
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='incoming_seller_conversations',
        limit_choices_to={'role': 'agent'},
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='seller_conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('customer', 'seller', 'product')
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat: {self.customer.username} -> {self.seller.username} ({self.product.title})"


class SellerMessage(models.Model):
    """Message within a seller conversation."""
    conversation = models.ForeignKey(SellerConversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_seller_messages')
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Msg by {self.sender.username} in chat #{self.conversation_id}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('return_requested', 'Return Requested'),
        ('return_approved', 'Return Approved'),
        ('returned', 'Returned'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='orders')
    delivery_address = models.ForeignKey('Address', null=True, blank=True, on_delete=models.SET_NULL)
    payment_method = models.ForeignKey('PaymentMethod', null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    def total(self):
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"Order #{self.id} by {self.user.username if self.user else 'Guest'}"


class OrderItem(models.Model):
    RETURN_STATUS_CHOICES = [
        ('none', 'No Return'),
        ('requested', 'Return Requested'),
        ('approved', 'Return Approved'),
        ('completed', 'Return Completed'),
    ]
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    quantity_returned = models.PositiveIntegerField(default=0)
    return_status = models.CharField(max_length=20, choices=RETURN_STATUS_CHOICES, default='none')
    return_reason = models.TextField(blank=True)
    requested_at = models.DateTimeField(null=True, blank=True)

    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.title} x {self.quantity} in Order #{self.order.id}"


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='cart', on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"


class SiteSettings(models.Model):
    site_title = models.CharField(max_length=200, default="Bhrikutimandap")
    site_description = models.TextField(default="Premium products from local suppliers")
    logo = models.ImageField(upload_to='settings/', null=True, blank=True)
    favicon = models.ImageField(upload_to='settings/', null=True, blank=True)
    
    # Logo Settings
    logo_height = models.IntegerField(default=0, help_text="Logo height in pixels. Set to 0 for auto.")
    logo_width = models.IntegerField(default=200, help_text="Logo width in pixels. Set to 0 for auto.")
    
    # Colors
    primary_color = models.CharField(max_length=7, default="#6c5ce7")
    secondary_color = models.CharField(max_length=7, default="#00b894")
    
    # Footer & Contact
    footer_text = models.TextField(default="© 2025 Bhrikutimandap. All rights reserved.")
    contact_email = models.EmailField(default="contact@bhrikutimandap.com")
    contact_phone = models.CharField(max_length=20, default="+123 456 7890")

    # Social links
    facebook_url = models.URLField(max_length=500, blank=True, default="")
    instagram_url = models.URLField(max_length=500, blank=True, default="")
    tiktok_url = models.URLField(max_length=500, blank=True, default="")
    youtube_url = models.URLField(max_length=500, blank=True, default="")
    twitter_url = models.URLField(max_length=500, blank=True, default="")
    linkedin_url = models.URLField(max_length=500, blank=True, default="")
    whatsapp_url = models.URLField(
        max_length=500,
        blank=True,
        default="",
        help_text="Full WhatsApp URL (e.g., https://wa.me/<number> or https://api.whatsapp.com/send?phone=<number>)",
    )
    
    # Store info
    store_address = models.TextField(default="123 Main Street, Your City")
    store_hours = models.CharField(max_length=100, default="Mon-Fri: 9am-6pm")
    
    # Home Page Text
    home_trending_title = models.CharField(max_length=200, default="Trending Product", help_text="Title for trending section")
    home_trending_subtitle = models.CharField(max_length=200, default="Popular Item in the market", help_text="Subtitle for trending section")
    home_bestseller_title = models.CharField(max_length=200, default="Best Sellers Shop", help_text="Title for best seller section")
    home_bestseller_subtitle = models.CharField(max_length=200, default="Amazon global bestselling products", help_text="Subtitle for best seller section")
    
    google_analytics_id = models.CharField(max_length=50, blank=True, default="", help_text="GA Measurement ID (e.g., G-XXXXXXXXXX)")

    # Email Configuration (SMTP)
    email_host = models.CharField(
        max_length=255,
        default="smtp.hostinger.com",
        help_text="SMTP server host (e.g., smtp.hostinger.com)"
    )
    email_port = models.PositiveIntegerField(
        default=587,
        help_text="SMTP port (usually 587 for TLS or 465 for SSL)"
    )
    email_use_tls = models.BooleanField(
        default=True,
        help_text="Use TLS for SMTP connection"
    )
    email_host_user = models.EmailField(
        default="admin@bhrikutimandap.com",
        help_text="SMTP username (usually your email address)"
    )
    email_host_password = models.CharField(
        max_length=255,
        default="",
        blank=True,
        help_text="SMTP password (stored securely)"
    )
    default_from_email = models.EmailField(
        default="admin@bhrikutimandap.com",
        help_text="Default sender email address"
    )
    
    # Legal Content (Rich Text / Long Text)
    terms_and_conditions = models.TextField(
        blank=True, 
        default="", 
        help_text="Full Terms and Conditions text. Standard HTML or plain text."
    )
    privacy_policy = models.TextField(
        blank=True, 
        default="", 
        help_text="Full Privacy Policy text. Standard HTML or plain text."
    )
    
    # Meta
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"

    @classmethod
    def get_instance(cls):
        instance, _ = cls.objects.get_or_create(pk=1)
        return instance


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    default_address = models.TextField(blank=True)
    phone_visible_to_agents = models.BooleanField(default=False)
    email_visible_to_agents = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


class Address(models.Model):
    """
    Delivery address management for customers
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=50, help_text="e.g., Home, Office, Parents")
    recipient_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='India')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.label} - {self.recipient_name}"

    def full_address(self):
        """Return formatted full address"""
        address = f"{self.address_line1}"
        if self.address_line2:
            address += f", {self.address_line2}"
        address += f", {self.city}, {self.state} {self.postal_code}, {self.country}"
        return address


class PaymentMethod(models.Model):
    """
    Store payment method tokens (not raw card data)
    Only stores tokenized payment information
    """
    PAYMENT_TYPE_CHOICES = [
        ('card', 'Credit/Debit Card'),
        ('upi', 'UPI'),
        ('netbanking', 'Net Banking'),
        ('wallet', 'Digital Wallet'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    
    # Tokenized payment info (never store raw card data)
    token = models.CharField(max_length=255, help_text="Payment gateway token (not raw card data)")
    
    # Display info (safe to store)
    display_name = models.CharField(max_length=100, help_text="e.g., 'Visa ending in 4242'")
    last_four = models.CharField(max_length=4, blank=True, help_text="Last 4 digits of card/account")
    
    # Metadata
    is_default = models.BooleanField(default=False)
    expiry_month = models.PositiveIntegerField(null=True, blank=True)
    expiry_year = models.PositiveIntegerField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.display_name} ({self.user.username})"

    def is_expired(self):
        """Check if payment method is expired"""
        if self.expiry_month and self.expiry_year:
            from datetime import datetime
            today = datetime.today()
            return (self.expiry_year < today.year) or \
                   (self.expiry_year == today.year and self.expiry_month < today.month)
        return False


class PaymentGatewayConfig(models.Model):
    class GatewayName(models.TextChoices):
        STRIPE = 'stripe', 'Stripe'
        KHALTI = 'khalti', 'Khalti'
        AILEPAY = 'ailepay', 'AilePay'
        DUMMY = 'dummy', 'Dummy (Local Test)'

    class Environment(models.TextChoices):
        SANDBOX = 'sandbox', 'Sandbox'
        PRODUCTION = 'production', 'Production'

    name = models.CharField(max_length=20, choices=GatewayName.choices, unique=True)
    is_enabled = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    environment = models.CharField(max_length=20, choices=Environment.choices, default=Environment.SANDBOX)
    config_json = models.TextField(default='{}', help_text='Encrypted gateway configuration payload')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Payment Gateway Config'
        verbose_name_plural = 'Payment Gateway Configs'

    def __str__(self):
        return f"{self.get_name_display()} ({self.environment})"

    @staticmethod
    def _get_fernet() -> Fernet:
        source = (
            getattr(settings, 'PAYMENT_CONFIG_ENCRYPTION_KEY', '')
            or settings.SECRET_KEY
        )
        digest = hashlib.sha256(source.encode('utf-8')).digest()
        key = base64.urlsafe_b64encode(digest)
        return Fernet(key)

    @classmethod
    def encrypt_config(cls, value: dict) -> str:
        payload = json.dumps(value or {}, separators=(',', ':'), sort_keys=True).encode('utf-8')
        token = cls._get_fernet().encrypt(payload).decode('utf-8')
        return f"enc::{token}"

    @classmethod
    def decrypt_config(cls, value: str) -> dict:
        if not value:
            return {}

        text = value.strip()
        if not text:
            return {}

        if text.startswith('enc::'):
            token = text[5:].encode('utf-8')
            try:
                decrypted = cls._get_fernet().decrypt(token)
            except InvalidToken:
                return {}
            try:
                return json.loads(decrypted.decode('utf-8'))
            except json.JSONDecodeError:
                return {}

        # Backward-compatible fallback for non-encrypted legacy values
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {}

    def get_config(self) -> dict:
        return self.decrypt_config(self.config_json)

    def set_config(self, value: dict) -> None:
        self.config_json = self.encrypt_config(value)

    def get_active_config(self) -> dict:
        config = self.get_config()
        return config.get(self.environment, {})

    def get_public_config(self) -> dict:
        active = self.get_active_config()
        if self.name == self.GatewayName.STRIPE:
            return {'publishable_key': active.get('publishable_key', '')}
        if self.name == self.GatewayName.KHALTI:
            return {'public_key': active.get('public_key', '')}
        if self.name == self.GatewayName.AILEPAY:
            return {'merchant_id': active.get('merchant_id', '')}
        if self.name == self.GatewayName.DUMMY:
            return {'mode': 'local-test'}
        return {}

    def clean(self):
        if self.is_default and not self.is_enabled:
            raise ValidationError('Default gateway must be enabled.')

    def save(self, *args, **kwargs):
        if self.is_default:
            PaymentGatewayConfig.objects.exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class PaymentTransaction(models.Model):
    class GatewayName(models.TextChoices):
        STRIPE = 'stripe', 'Stripe'
        KHALTI = 'khalti', 'Khalti'
        AILEPAY = 'ailepay', 'AilePay'
        DUMMY = 'dummy', 'Dummy (Local Test)'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'

    order = models.ForeignKey('Order', null=True, blank=True, on_delete=models.SET_NULL, related_name='payment_transactions')
    gateway = models.CharField(max_length=20, choices=GatewayName.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='NPR')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    external_id = models.CharField(max_length=255, blank=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)
    verification_attempts = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['gateway', 'status']),
            models.Index(fields=['external_id']),
        ]

    def __str__(self):
        return f"{self.gateway} {self.amount} {self.currency} ({self.status})"


class PaymentGatewayAudit(models.Model):
    class Action(models.TextChoices):
        CREATED = 'created', 'Created'
        UPDATED = 'updated', 'Updated'
        VALIDATED = 'validated', 'Validated'
        ENABLED = 'enabled', 'Enabled'
        DISABLED = 'disabled', 'Disabled'
        CREATE_PAYMENT = 'create_payment', 'Create Payment'
        VERIFY_PAYMENT = 'verify_payment', 'Verify Payment'
        WEBHOOK_VERIFY = 'webhook_verify', 'Webhook Verify'
        WEBHOOK_ERROR = 'webhook_error', 'Webhook Error'

    gateway = models.ForeignKey(PaymentGatewayConfig, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    action = models.CharField(max_length=32, choices=Action.choices)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        who = self.actor.username if self.actor else 'system'
        return f"{self.action} by {who}"


class Wishlist(models.Model):
    """
    User's wishlist containing favorite products
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wishlist of {self.user.username}"

    def item_count(self):
        return self.items.count()


class WishlistItem(models.Model):
    """
    Individual products in a user's wishlist
    """
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['wishlist', 'product']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.product.title} in {self.wishlist.user.username}'s wishlist"


# ==================== AGENT/SUPPLIER PORTAL MODELS ====================

class AgentProfile(models.Model):
    """
    Extended profile for agent/supplier users
    """
    APPROVAL_STATUS = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile')
    company_name = models.CharField(max_length=200, blank=True)
    company_address = models.TextField(blank=True)
    company_phone = models.CharField(max_length=20, blank=True)
    gst_number = models.CharField(max_length=50, blank=True, unique=True, null=True)
    bank_account = models.CharField(max_length=50, blank=True)
    bank_ifsc = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS, default='pending')
    monthly_target = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # Logo and branding images
    company_logo = models.ImageField(upload_to='agent/logos/', null=True, blank=True, help_text='Company logo image')
    company_banner = models.ImageField(upload_to='agent/banners/', null=True, blank=True, help_text='Company banner image')
    trademark_image = models.ImageField(upload_to='agent/trademarks/', null=True, blank=True, help_text='Trademark or certification image')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"AgentProfile: {self.user.username} ({self.approval_status})"


class StockHistory(models.Model):
    """
    Track all stock changes for audit and analysis
    """
    ACTION_CHOICES = [
        ('increase', 'Stock Increase'),
        ('decrease', 'Stock Decrease'),
        ('adjustment', 'Manual Adjustment'),
        ('return', 'Return from Customer'),
        ('damage', 'Damage/Loss'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_history')
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    quantity_changed = models.IntegerField()
    old_quantity = models.PositiveIntegerField()
    new_quantity = models.PositiveIntegerField()
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Stock Histories'
    
    def __str__(self):
        return f"{self.product.title}: {self.action} ({self.quantity_changed}) on {self.created_at.date()}"


class SalesTransaction(models.Model):
    """
    Record individual sales transactions for analytics
    """
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales_transactions')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_transactions')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_transactions')
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"Sale: {self.product.title} x{self.quantity} on {self.transaction_date.date()}"
    
    def save(self, *args, **kwargs):
        """Auto-calculate total_amount"""
        if not self.total_amount:
            self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class StockAlert(models.Model):
    """
    Low stock alerts to notify agent when stock is below threshold
    """
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stock_alerts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_alerts')
    threshold_quantity = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['agent', 'product']
    
    def __str__(self):
        return f"Alert: {self.product.title} < {self.threshold_quantity}"
    
    def is_triggered(self):
        """Check if current stock is below threshold"""
        return self.product.stock < self.threshold_quantity


class MarketDemandSuggestion(models.Model):
    """
    AI-driven suggestions for market demand analysis
    Initially rule-based, designed for ML/LLM integration
    """
    SUGGESTION_TYPES = [
        ('trending', 'Trending (Increasing Demand)'),
        ('declining', 'Declining (Decreasing Demand)'),
        ('opportunity', 'New Opportunity'),
        ('seasonal', 'Seasonal Pattern'),
    ]
    
    DATA_PERIODS = [
        ('7_days', 'Last 7 Days'),
        ('30_days', 'Last 30 Days'),
        ('90_days', 'Last 90 Days'),
    ]
    
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='demand_suggestions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='demand_suggestions')
    suggestion_type = models.CharField(max_length=20, choices=SUGGESTION_TYPES)
    confidence_score = models.FloatField(default=0.5)  # 0.0 to 1.0
    reason = models.TextField()
    data_period = models.CharField(max_length=20, choices=DATA_PERIODS, default='30_days')
    is_actioned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_suggestion_type_display()}: {self.product.title}"

# ==================== DELIVERY & LOGISTICS MODELS ====================

class DeliveryPartner(models.Model):
    """
    Delivery partners/couriers available for shipment
    Agents can assign orders to delivery partners
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
    ]
    
    name = models.CharField(max_length=200)
    contact_name = models.CharField(max_length=200, blank=True, help_text="Primary contact person name")
    phone = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    current_location = models.CharField(max_length=255, blank=True, help_text="City/Area of operation")
    avg_delivery_time_hours = models.PositiveIntegerField(default=24, help_text="Estimated delivery time in hours")
    success_delivery_rate = models.FloatField(default=95.0, help_text="Percentage of successful deliveries")
    total_deliveries = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['status', 'name']
    
    def __str__(self):
        return f"{self.name}"
    
    def is_available(self):
        return self.status == 'active'
    
    def get_primary_vehicle(self):
        """Get the primary/first vehicle"""
        return self.vehicles.first()


class Vehicle(models.Model):
    """
    Vehicles associated with a delivery partner
    Allows delivery partners to have multiple vehicles
    """
    VEHICLE_TYPE_CHOICES = [
        ('bike', 'Two-wheeler'),
        ('auto', 'Auto-rickshaw'),
        ('car', 'Car'),
        ('truck', 'Truck'),
        ('van', 'Van'),
    ]
    
    delivery_partner = models.ForeignKey(DeliveryPartner, on_delete=models.CASCADE, related_name='vehicles')
    vehicle_type = models.CharField(max_length=50, choices=VEHICLE_TYPE_CHOICES)
    vehicle_number = models.CharField(max_length=20, unique=True)
    model = models.CharField(max_length=100, blank=True, help_text="Vehicle model/name")
    registration_number = models.CharField(max_length=50, blank=True)
    capacity = models.CharField(max_length=100, blank=True, help_text="e.g., 50kg, 100kg")
    insured = models.BooleanField(default=False)
    insurance_expiry = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('maintenance', 'Under Maintenance'),
        ('inactive', 'Inactive'),
    ], default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-status', '-created_at']
        verbose_name_plural = 'Vehicles'
    
    def __str__(self):
        return f"{self.get_vehicle_type_display()} - {self.vehicle_number} ({self.delivery_partner.name})"
    
    def is_available(self):
        return self.status == 'active' and self.delivery_partner.status == 'active'


class OrderDelivery(models.Model):
    """
    Links an Order to a DeliveryPartner
    Tracks the delivery assignment and current status
    """
    DELIVERY_STATUS_CHOICES = [
        ('not_assigned', 'Not Assigned'),
        ('assigned', 'Assigned'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('delivery_failed', 'Delivery Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    delivery_partner = models.ForeignKey(DeliveryPartner, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_deliveries', limit_choices_to={'role': 'agent'})
    
    # Delivery details
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default='not_assigned')
    assigned_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    actual_delivery = models.DateTimeField(null=True, blank=True)
    delivery_notes = models.TextField(blank=True)
    failed_reason = models.TextField(blank=True, help_text="Reason if delivery failed")
    
    # Tracking
    last_location = models.CharField(max_length=255, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Delivery of Order #{self.order.id} - {self.delivery_status}"
    
    def get_estimated_delivery(self):
        """Calculate estimated delivery time"""
        if self.assigned_at and self.delivery_partner:
            return self.assigned_at + timedelta(hours=self.delivery_partner.avg_delivery_time_hours)
        return None
    
    def is_delivered(self):
        return self.delivery_status == 'delivered'
    
    def mark_as_delivered(self):
        """Mark order as delivered"""
        if self.delivery_status in ['out_for_delivery', 'in_transit']:
            self.delivery_status = 'delivered'
            self.actual_delivery = timezone.now()
            self.save()
            # Update order status
            self.order.status = 'delivered'
            self.order.save()
            return True
        return False


class DeliveryTracking(models.Model):
    """
    Step-by-step tracking of delivery journey
    Creates the "pizza trajectory" - shows delivery progress
    """
    TRACKING_STAGE_CHOICES = [
        ('order_confirmed', 'Order Confirmed'),
        ('packed', 'Packed & Ready'),
        ('picked_up', 'Picked Up by Delivery Partner'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('return_initiated', 'Return Initiated'),
        ('return_in_transit', 'Return In Transit'),
        ('return_received', 'Return Received'),
    ]
    
    order_delivery = models.ForeignKey(OrderDelivery, on_delete=models.CASCADE, related_name='tracking_stages')
    stage = models.CharField(max_length=30, choices=TRACKING_STAGE_CHOICES)
    stage_timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255, blank=True, help_text="Location at this stage")
    notes = models.TextField(blank=True, help_text="Additional notes for this stage")
    image = models.ImageField(upload_to='tracking/', null=True, blank=True, help_text="Photo proof if applicable")
    
    class Meta:
        ordering = ['stage_timestamp']
        verbose_name_plural = 'Delivery Tracking'
    
    def __str__(self):
        return f"{self.order_delivery.order.id}: {self.get_stage_display()}"


class ReturnRequest(models.Model):
    """
    Handle product returns from customers
    Tracks the return process and status
    """
    RETURN_STATUS_CHOICES = [
        ('requested', 'Return Requested'),
        ('approved', 'Return Approved'),
        ('rejected', 'Return Rejected'),
        ('in_transit', 'Return In Transit'),
        ('received', 'Return Received'),
        ('refunded', 'Refunded'),
    ]
    
    RETURN_REASON_CHOICES = [
        ('defective', 'Defective/Damaged'),
        ('wrong_item', 'Wrong Item Received'),
        ('not_as_described', 'Not as Described'),
        ('changed_mind', 'Changed Mind'),
        ('other', 'Other'),
    ]
    
    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE, related_name='return_request')
    return_reason = models.CharField(max_length=30, choices=RETURN_REASON_CHOICES)
    return_description = models.TextField(help_text="Detailed reason for return")
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=RETURN_STATUS_CHOICES, default='requested')
    
    # Return tracking
    return_delivery = models.OneToOneField(OrderDelivery, on_delete=models.SET_NULL, null=True, blank=True, related_name='return_request')
    received_at = models.DateTimeField(null=True, blank=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    
    # Agent notes
    agent_notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_returns', limit_choices_to={'role': 'agent'})
    approved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"Return: Order #{self.order_item.order.id} - {self.get_status_display()}"
    
    def is_approved(self):
        return self.status in ['approved', 'in_transit', 'received', 'refunded']
    
    def approve_return(self, agent, notes=''):
        """Approve a return request"""
        self.status = 'approved'
        self.approved_by = agent
        self.approved_at = timezone.now()
        if notes:
            self.agent_notes = notes
        self.save()


class AgentDeliveryPartner(models.Model):
    """
    Links agents to delivery partners they prefer to work with
    Allows agents to configure and manage their delivery methods
    """
    agent = models.ForeignKey(AgentProfile, on_delete=models.CASCADE, related_name='delivery_partners')
    delivery_partner = models.ForeignKey(DeliveryPartner, on_delete=models.CASCADE, related_name='agent_preferences')
    is_preferred = models.BooleanField(default=False, help_text="Mark as preferred delivery partner")
    is_active = models.BooleanField(default=True, help_text="Is this delivery partner active for this agent?")
    notes = models.TextField(blank=True, help_text="Special instructions or notes for this partner")
    assigned_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('agent', 'delivery_partner')
        ordering = ['-is_preferred', '-is_active', 'delivery_partner__name']
    
    def __str__(self):
        return f"{self.agent.company_name} - {self.delivery_partner.name}"


class Blog(models.Model):
    """Blog posts for the website"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, help_text="URL-friendly version of the title")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blogs')
    content = models.TextField()  # Will use RichTextUploadingField in admin
    featured_image = models.ImageField(upload_to='blog/', null=True, blank=True)
    excerpt = models.TextField(max_length=500, blank=True, help_text="Short summary for blog listing")
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
    
    def __str__(self):
        return self.title


class EmailTemplate(models.Model):
    """Email templates that can be edited from admin"""
    TEMPLATE_TYPES = [
        ('activation', 'Account Activation'),
        ('contact_admin', 'Contact Form to Admin'),
        ('password_reset', 'Password Reset'),
        ('welcome', 'Welcome Email'),
        ('otp_verification', 'OTP Verification'),
    ]
    
    name = models.CharField(max_length=100, unique=True, help_text="Internal name (e.g., 'activation', 'contact_admin')")
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPES)
    subject = models.CharField(
        max_length=200, 
        help_text="Email subject. Use variables like {username}, {email}, etc."
    )
    body = models.TextField(
        help_text="""Email body template. Available variables depend on template type:
        
Activation: {username}, {email}, {user_id}, {activation_link}
Contact Admin: {name}, {email}, {phone}, {subject_input}, {message}
Password Reset: {username}, {email}, {reset_link}
Welcome: {username}, {email}
OTP Verification: {username}, {otp}, {logo_url}, {site_title}
        """
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Email Template"
        verbose_name_plural = "Email Templates"
    
    def __str__(self):
        return f"{self.get_template_type_display()} - {self.name}"
    
    def render(self, **context):
        """Render the email template with context variables, automatically injecting SiteSettings."""
        try:
            # Inject global site settings if not present
            if 'logo_url' not in context or 'site_title' not in context:
                from .models import SiteSettings
                from django.conf import settings
                site_settings = SiteSettings.get_instance()
                
                if 'site_title' not in context:
                    context['site_title'] = site_settings.site_title
                
                if 'logo_url' not in context:
                    if site_settings.logo:
                        # Use Content-ID for inline image embedding
                        context['logo_url'] = "cid:logo"
                    else:
                        context['logo_url'] = ""

            return self.body.format(**context)
        except KeyError as e:
            # Return a friendly error in the email itself (or log it)
            # returning the original body might be safer than crashing
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Template rendering error: Missing variable {e}")
            return self.body  # Fallback to unrendered body or a safe error message
        except Exception as e:
             return f"[Template Error: {e}]"

    def render_subject(self, **context):
        """Render the email subject with context variables."""
        try:
            # Inject global site settings if not present
            if 'site_title' not in context:
                from .models import SiteSettings
                site_settings = SiteSettings.get_instance()
                context['site_title'] = site_settings.site_title
                
            return self.subject.format(**context)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Subject rendering error: {e}")
            return self.subject


# Signal handlers for User role management
from django.db.models.signals import pre_save
from django.dispatch import receiver


@receiver(pre_save, sender=User)
def update_user_permissions_on_role_change(sender, instance, **kwargs):
    """
    Automatically set is_staff and is_superuser when role is set to 'admin'.
    Remove these flags when role is changed from 'admin' to something else.
    """
    if instance.role == 'admin':
        instance.is_staff = True
        instance.is_superuser = True
    elif instance.role != 'admin':
        # Only reset if they're explicitly changing FROM admin to something else
        # Check if this is an existing user and their role is changing
        try:
            old_instance = User.objects.get(pk=instance.pk)
            if old_instance.role == 'admin':
                instance.is_staff = False
                instance.is_superuser = False
        except User.DoesNotExist:
            # New user, not changing from admin
            pass
class SEOModel(models.Model):
    meta_title = models.CharField(max_length=255, blank=True, help_text='SEO Title')
    meta_description = models.TextField(blank=True, help_text='SEO Description')
    meta_keywords = models.CharField(max_length=255, blank=True, help_text='SEO Keywords (comma separated)')

    class Meta:
        abstract = True

class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class HomePage(SEOModel, SingletonModel):
    featured_title = models.CharField(max_length=200, default='Featured Picks')
    featured_subtitle = models.CharField(max_length=255, default='Handpicked highlights from verified sellers.')
    trending_title = models.CharField(max_length=200, default='Trending Product')
    trending_subtitle = models.CharField(max_length=200, default='Popular Item in the market')
    best_seller_title = models.CharField(max_length=200, default='Best Sellers Shop')
    best_seller_subtitle = models.CharField(max_length=200, default='Amazon global bestselling products')

    class Meta:
        verbose_name = 'Home Page Settings'
        verbose_name_plural = 'Home Page Settings'

class ContactPage(SEOModel, SingletonModel):
    map_url = models.URLField(max_length=500, blank=True, help_text='Google Maps Embed URL')
    contact_title = models.CharField(max_length=200, default='Contact Us')
    success_message = models.TextField(default='Message sent successfully!')
    
    class Meta:
        verbose_name = 'Contact Page Settings'
        verbose_name_plural = 'Contact Page Settings'

class AuthPage(SEOModel, SingletonModel):
    login_title = models.CharField(max_length=200, default='Login to your account')
    register_title = models.CharField(max_length=200, default='Create an Account')
    login_banner_text = models.TextField(default='New to our website?')
    register_banner_text = models.TextField(default='Already have an account?')

    class Meta:
        verbose_name = 'Auth Page Settings'
        verbose_name_plural = 'Auth Page Settings'

class ProductPageSettings(SEOModel, SingletonModel):
    add_to_cart_label = models.CharField(max_length=50, default='Add to Cart')
    out_of_stock_label = models.CharField(max_length=50, default='Out of Stock')
    description_tab_label = models.CharField(max_length=50, default='Description')
    reviews_tab_label = models.CharField(max_length=50, default='Reviews')

    class Meta:
        verbose_name = 'Product Page Settings'
        verbose_name_plural = 'Product Page Settings'

class AgentPageSettings(SEOModel, SingletonModel):
    dashboard_welcome_title = models.CharField(max_length=200, default='Agent Dashboard')
    add_product_button_label = models.CharField(max_length=50, default='Add New Product')
    products_table_header = models.CharField(max_length=100, default='Your Products')

    class Meta:
        verbose_name = 'Agent Page Settings'
        verbose_name_plural = 'Agent Page Settings'


# Signals
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'agent':
        AgentProfile.objects.get_or_create(
            user=instance,
            defaults={'company_name': instance.company or ''}
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == 'agent' and hasattr(instance, 'agent_profile'):
        profile = instance.agent_profile
        if instance.company and not profile.company_name:
            profile.company_name = instance.company
        # Sync approval status from User to Profile
        if instance.approved_by_admin:
            profile.approval_status = 'approved'
            profile.is_verified = True
        profile.save()
