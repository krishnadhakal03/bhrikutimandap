import io
import os
import zipfile
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone
from django.utils.html import format_html
from .models import (
    User, Product, ProductImage, Order, OrderItem, Cart, CartItem, SiteSettings, 
    CustomerProfile, Address, PaymentMethod, Wishlist, WishlistItem,
    AgentProfile, StockHistory, SalesTransaction, StockAlert, MarketDemandSuggestion,
    DeliveryPartner, Vehicle, OrderDelivery, DeliveryTracking, ReturnRequest
)


# Custom Admin Site Styling
admin.site.site_header = "🛍️ Bhrikutimandap Administration"
admin.site.site_title = "Bhrikutimandap Admin"
admin.site.index_title = "Welcome to Bhrikutimandap Admin Panel"


def _admin_db_tools_view(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    backup_dir = os.environ.get('ADMIN_BACKUP_DIR') or str(settings.BASE_DIR / 'backups')
    os.makedirs(backup_dir, exist_ok=True)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create_server_dump':
            stamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            filename = f'bhrikutimandap_fixture_{stamp}.json'
            out_path = os.path.join(backup_dir, filename)
            try:
                with open(out_path, 'w', encoding='utf-8') as fp:
                    call_command(
                        'dumpdata',
                        '--natural-foreign',
                        '--natural-primary',
                        '--exclude',
                        'contenttypes',
                        '--exclude',
                        'auth.permission',
                        '--exclude',
                        'admin.logentry',
                        '--indent',
                        '2',
                        stdout=fp,
                    )
                messages.success(request, f'Server backup created: {filename}')
            except Exception as exc:
                messages.error(request, f'Backup failed: {exc}')

        if action == 'download_server_dump':
            requested = (request.POST.get('filename') or '').strip()
            safe_name = os.path.basename(requested)
            if not safe_name or safe_name != requested or not safe_name.endswith('.json'):
                messages.error(request, 'Invalid backup filename.')
            else:
                file_path = os.path.join(backup_dir, safe_name)
                if not os.path.isfile(file_path):
                    messages.error(request, 'Backup file not found.')
                else:
                    with open(file_path, 'rb') as fp:
                        payload = fp.read()
                    resp = HttpResponse(payload, content_type='application/json; charset=utf-8')
                    resp['Content-Disposition'] = f'attachment; filename="{safe_name}"'
                    return resp

        if action == 'dump_json':
            out = io.StringIO()
            call_command(
                'dumpdata',
                '--natural-foreign',
                '--natural-primary',
                '--exclude',
                'contenttypes',
                '--exclude',
                'auth.permission',
                '--exclude',
                'admin.logentry',
                '--indent',
                '2',
                stdout=out,
            )
            payload = out.getvalue().encode('utf-8')
            stamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            resp = HttpResponse(payload, content_type='application/json; charset=utf-8')
            resp['Content-Disposition'] = f'attachment; filename="bhrikutimandap_dump_{stamp}.json"'
            return resp

        if action == 'download_media_zip':
            media_root = str(settings.MEDIA_ROOT)
            if not os.path.isdir(media_root):
                messages.warning(request, f"MEDIA_ROOT not found: {media_root}")
            else:
                buf = io.BytesIO()
                with zipfile.ZipFile(buf, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
                    for root, _dirs, files in os.walk(media_root):
                        for filename in files:
                            abs_path = os.path.join(root, filename)
                            rel_path = os.path.relpath(abs_path, media_root)
                            zf.write(abs_path, arcname=rel_path)
                buf.seek(0)
                stamp = timezone.now().strftime('%Y%m%d_%H%M%S')
                resp = HttpResponse(buf.getvalue(), content_type='application/zip')
                resp['Content-Disposition'] = f'attachment; filename="bhrikutimandap_media_{stamp}.zip"'
                return resp

        if action == 'load_json':
            uploaded = request.FILES.get('fixture')
            if not uploaded:
                messages.error(request, 'Please choose a .json file to load.')
            else:
                with NamedTemporaryFile(delete=False, suffix='.json') as tmp:
                    for chunk in uploaded.chunks():
                        tmp.write(chunk)
                    tmp_path = tmp.name
                try:
                    call_command('loaddata', tmp_path)
                    messages.success(request, 'Data loaded successfully.')
                except Exception as exc:
                    messages.error(request, f'Load failed: {exc}')
                finally:
                    try:
                        os.remove(tmp_path)
                    except OSError:
                        pass

    context = {
        **admin.site.each_context(request),
        'title': 'DB Tools',
        'media_root': str(settings.MEDIA_ROOT),
        'backup_dir': backup_dir,
        'server_backups': _list_server_backups(backup_dir),
    }
    return TemplateResponse(request, 'admin/db_tools.html', context)


def _list_server_backups(backup_dir: str) -> list[str]:
    try:
        candidates: list[tuple[float, str]] = []
        for name in os.listdir(backup_dir):
            if not name.endswith('.json'):
                continue
            path = os.path.join(backup_dir, name)
            if not os.path.isfile(path):
                continue
            candidates.append((os.path.getmtime(path), name))
        candidates.sort(reverse=True)
        return [name for _mtime, name in candidates[:20]]
    except Exception:
        return []


_original_admin_get_urls = admin.site.get_urls


def _admin_get_urls_with_tools():
    urls = _original_admin_get_urls()
    custom = [
        path('db-tools/', admin.site.admin_view(_admin_db_tools_view), name='db_tools'),
    ]
    return custom + urls


admin.site.get_urls = _admin_get_urls_with_tools


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role_badge', 'phone', 'company', 'approval_badge', 'status_badge')
    list_filter = ('role', 'approved_by_admin', 'verified', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'company')
    list_per_page = 25
    date_hierarchy = 'date_joined'
    actions = ['approve_users', 'deactivate_users', 'activate_users']

    fieldsets = (
        ('Account', {'fields': ('username', 'email', 'password')}),
        ('Personal', {'fields': ('first_name', 'last_name', 'phone', 'company')}),
        ('Address', {'fields': ('address_line1', 'address_line2', 'city', 'state', 'country', 'postal_code')}),
        ('Role & Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'verified', 'approved_by_admin')}),
        ('Dates', {'fields': ('date_joined', 'last_login'), 'classes': ('collapse',)}),
    )

    def role_badge(self, obj):
        colors = {
            'customer': '#2196F3',
            'agent': '#4CAF50',
            'admin': '#FF9800',
        }
        color = colors.get(obj.role, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_role_display()
        )
    role_badge.short_description = 'Role'

    def approval_badge(self, obj):
        if obj.approved_by_admin:
            return format_html('<span style="color: green; font-weight: bold;">✓ Approved</span>')
        return format_html('<span style="color: orange; font-weight: bold;">⧖ Pending</span>')
    approval_badge.short_description = 'Approval Status'

    def status_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #4CAF50; font-weight: bold;">● Active</span>')
        return format_html('<span style="color: #f44336; font-weight: bold;">● Inactive</span>')
    status_badge.short_description = 'Status'

    def approve_users(self, request, queryset):
        updated = queryset.update(approved_by_admin=True)
        self.message_user(request, f'{updated} user(s) approved successfully.')
    approve_users.short_description = 'Approve selected users'

    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} user(s) deactivated.')
    deactivate_users.short_description = 'Deactivate selected users'

    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user(s) activated.')
    activate_users.short_description = 'Activate selected users'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'supplier', 'price_display', 'stock_status', 'image_preview', 'created_at')
    list_filter = ('supplier', 'created_at', 'stock')
    search_fields = ('title', 'description', 'supplier__username')
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    list_per_page = 25
    date_hierarchy = 'created_at'
    actions = ['mark_in_stock', 'mark_out_of_stock']
    
    fieldsets = (
        ('Product Information', {
            'fields': ('supplier', 'title', 'description', 'price'),
            'classes': ('wide',)
        }),
        ('Inventory Management', {
            'fields': ('stock', 'expiration_date', 'is_in_stock'),
            'classes': ('wide',)
        }),
        ('Delivery & Payment', {
            'fields': ('delivery_rules', 'payment_methods'),
            'classes': ('wide',)
        }),
        ('Media', {
            'fields': ('image', 'image_preview'),
            'classes': ('wide',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def price_display(self, obj):
        return format_html('<span style="color: #2e7d32; font-weight: bold;">₹{}</span>', obj.price)
    price_display.short_description = 'Price'

    def stock_status(self, obj):
        if obj.stock > 0:
            color = '#4CAF50'
            status = f'In Stock ({obj.stock})'
        else:
            color = '#f44336'
            status = 'Out of Stock'
        return format_html(
            '<span style="color: {}; font-weight: bold;">● {}</span>',
            color,
            status
        )
    stock_status.short_description = 'Stock Status'

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:80px; width:80px; border-radius: 4px; object-fit: cover;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">No image</span>')
    image_preview.allow_tags = True
    image_preview.short_description = 'Preview'

    def mark_in_stock(self, request, queryset):
        updated = queryset.update(is_in_stock=True)
        self.message_user(request, f'{updated} product(s) marked as in stock.')
    mark_in_stock.short_description = 'Mark selected as in stock'

    def mark_out_of_stock(self, request, queryset):
        updated = queryset.update(is_in_stock=False)
        self.message_user(request, f'{updated} product(s) marked as out of stock.')
    mark_out_of_stock.short_description = 'Mark selected as out of stock'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'uploaded_at', 'image_preview')
    list_filter = ('uploaded_at',)
    search_fields = ('product__title',)
    readonly_fields = ('uploaded_at', 'image_preview')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:60px; width:60px; border-radius: 4px; object-fit: cover;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">No image</span>')
    image_preview.allow_tags = True


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'status_badge', 'payment_badge', 'total_display', 'created_at')
    list_filter = ('status', 'paid', 'created_at')
    search_fields = ('id', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'total_display')
    list_per_page = 25
    date_hierarchy = 'created_at'
    actions = ['mark_as_pending', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_paid']
    
    inlines = [OrderItemInline]

    def order_id(self, obj):
        return format_html('<span style="font-weight: bold; color: #2e7d32;">#{}</span>', obj.id)
    order_id.short_description = 'Order ID'

    def status_badge(self, obj):
        colors = {
            'pending': '#FF9800',
            'processing': '#2196F3',
            'shipped': '#9C27B0',
            'delivered': '#4CAF50',
            'cancelled': '#f44336',
        }
        color = colors.get(obj.status, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def payment_badge(self, obj):
        if obj.paid:
            return format_html('<span style="color: #4CAF50; font-weight: bold;">✓ Paid</span>')
        return format_html('<span style="color: #FF9800; font-weight: bold;">⧖ Unpaid</span>')
    payment_badge.short_description = 'Payment'

    def total_display(self, obj):
        total = obj.total()
        return format_html('<span style="color: #2e7d32; font-weight: bold;">₹{}</span>', f'{total:.2f}')
    total_display.short_description = 'Total'

    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f'{updated} order(s) marked as pending.')
    mark_as_pending.short_description = 'Mark as Pending'

    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} order(s) marked as shipped.')
    mark_as_shipped.short_description = 'Mark as Shipped'

    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} order(s) marked as delivered.')
    mark_as_delivered.short_description = 'Mark as Delivered'

    def mark_as_paid(self, request, queryset):
        updated = queryset.update(paid=True)
        self.message_user(request, f'{updated} order(s) marked as paid.')
    mark_as_paid.short_description = 'Mark as Paid'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'user', 'item_count', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('updated_at',)
    
    def cart_id(self, obj):
        return format_html('<span style="font-weight: bold;">#{}</span>', obj.id)
    cart_id.short_description = 'Cart ID'

    def item_count(self, obj):
        count = obj.items.count()
        return format_html(
            '<span style="background: #2e7d32; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;">{} items</span>',
            count
        )
    item_count.short_description = 'Items'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity_display', 'get_total_price')
    list_filter = ('cart__updated_at',)
    search_fields = ('cart__user__username', 'product__title')
    readonly_fields = ('get_total_price',)

    def quantity_display(self, obj):
        return format_html(
            '<span style="background: #2196F3; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;">{} qty</span>',
            obj.quantity
        )
    quantity_display.short_description = 'Quantity'

    def get_total_price(self, obj):
        total = obj.product.price * obj.quantity
        return format_html('<span style="color: #2e7d32; font-weight: bold;">₹{}</span>', f'{total:.2f}')
    get_total_price.short_description = 'Total Price'


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Site Branding', {'fields': ('site_title', 'site_description', 'logo', 'favicon')}),
        ('Colors', {'fields': ('primary_color', 'secondary_color')}),
        ('Contact Info', {'fields': ('contact_email', 'contact_phone', 'store_address', 'store_hours')}),
        (
            'Social Links',
            {
                'fields': (
                    'facebook_url',
                    'instagram_url',
                    'tiktok_url',
                    'youtube_url',
                    'twitter_url',
                    'linkedin_url',
                    'whatsapp_url',
                )
            },
        ),
        ('Footer', {'fields': ('footer_text',)}),
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        try:
            obj = SiteSettings.objects.get(pk=1)
            extra_context['title'] = 'Site Settings'
        except SiteSettings.DoesNotExist:
            SiteSettings.objects.create(pk=1)
        return super().changelist_view(request, extra_context)


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_visibility_badge', 'email_visibility_badge')
    list_filter = ('phone_visible_to_agents', 'email_visible_to_agents')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user',)

    def phone_visibility_badge(self, obj):
        if obj.phone_visible_to_agents:
            return format_html('<span style="color: #4CAF50; font-weight: bold;">✓ Visible</span>')
        return format_html('<span style="color: #f44336; font-weight: bold;">✗ Hidden</span>')
    phone_visibility_badge.short_description = 'Phone Visible'

    def email_visibility_badge(self, obj):
        if obj.email_visible_to_agents:
            return format_html('<span style="color: #4CAF50; font-weight: bold;">✓ Visible</span>')
        return format_html('<span style="color: #f44336; font-weight: bold;">✗ Hidden</span>')
    email_visibility_badge.short_description = 'Email Visible'


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('label', 'user', 'city', 'state', 'default_badge')
    list_filter = ('city', 'state', 'is_default')
    search_fields = ('user__username', 'recipient_name', 'city', 'state')
    list_per_page = 25
    
    fieldsets = (
        ('Address Details', {
            'fields': ('user', 'label', 'recipient_name'),
            'classes': ('wide',)
        }),
        ('Location', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'country', 'postal_code'),
            'classes': ('wide',)
        }),
        ('Settings', {
            'fields': ('is_default',),
            'classes': ('wide',)
        }),
    )

    def default_badge(self, obj):
        if obj.is_default:
            return format_html('<span style="color: #4CAF50; font-weight: bold;">★ Default</span>')
        return format_html('<span style="color: #999;">-</span>')
    default_badge.short_description = 'Default'


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user', 'payment_type_badge', 'default_badge', 'status_badge')
    list_filter = ('payment_type', 'is_default', 'is_active')
    search_fields = ('user__username', 'display_name')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25

    def payment_type_badge(self, obj):
        colors = {'credit_card': '#2196F3', 'debit_card': '#4CAF50', 'upi': '#FF9800', 'wallet': '#9C27B0'}
        color = colors.get(obj.payment_type, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_payment_type_display()
        )
    payment_type_badge.short_description = 'Type'

    def default_badge(self, obj):
        if obj.is_default:
            return format_html('<span style="color: #4CAF50; font-weight: bold;">★ Default</span>')
        return format_html('<span style="color: #999;">-</span>')
    default_badge.short_description = 'Default'

    def status_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #4CAF50; font-weight: bold;">● Active</span>')
        return format_html('<span style="color: #f44336; font-weight: bold;">● Inactive</span>')
    status_badge.short_description = 'Status'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'items_count', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)

    def items_count(self, obj):
        count = obj.items.count()
        return format_html(
            '<span style="background: #FF9800; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;">{} items</span>',
            count
        )
    items_count.short_description = 'Items'


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'wishlist_user', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('product__title', 'wishlist__user__username')
    readonly_fields = ('added_at',)

    def wishlist_user(self, obj):
        return format_html('<span style="font-weight: bold;">{}</span>', obj.wishlist.user.username)
    wishlist_user.short_description = 'Wishlist Owner'


@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'status_badge', 'verification_badge', 'created_at')
    list_filter = ('approval_status', 'is_verified', 'created_at')
    search_fields = ('user__username', 'company_name', 'gst_number')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    date_hierarchy = 'created_at'
    actions = ['approve_agents', 'reject_agents', 'verify_agents']

    fieldsets = (
        ('Company Information', {
            'fields': ('user', 'company_name', 'gst_number', 'business_type'),
            'classes': ('wide',)
        }),
        ('Verification & Approval', {
            'fields': ('is_verified', 'approval_status'),
            'classes': ('wide',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'approved': '#4CAF50',
            'pending': '#FF9800',
            'rejected': '#f44336',
        }
        color = colors.get(obj.approval_status, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_approval_status_display()
        )
    status_badge.short_description = 'Approval Status'

    def verification_badge(self, obj):
        if obj.is_verified:
            return format_html('<span style="color: #4CAF50; font-weight: bold;">✓ Verified</span>')
        return format_html('<span style="color: #FF9800; font-weight: bold;">⧖ Pending</span>')
    verification_badge.short_description = 'Verification'

    def approve_agents(self, request, queryset):
        updated = queryset.update(approval_status='approved')
        self.message_user(request, f'{updated} agent(s) approved.')
    approve_agents.short_description = 'Approve selected agents'

    def reject_agents(self, request, queryset):
        updated = queryset.update(approval_status='rejected')
        self.message_user(request, f'{updated} agent(s) rejected.')
    reject_agents.short_description = 'Reject selected agents'

    def verify_agents(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} agent(s) verified.')
    verify_agents.short_description = 'Verify selected agents'


@admin.register(StockHistory)
class StockHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'agent', 'action_badge', 'quantity_display', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('product__title', 'agent__username')
    readonly_fields = ('created_at',)
    list_per_page = 25
    date_hierarchy = 'created_at'

    def action_badge(self, obj):
        colors = {'add': '#4CAF50', 'remove': '#f44336', 'adjust': '#FF9800'}
        color = colors.get(obj.action, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_action_display()
        )
    action_badge.short_description = 'Action'

    def quantity_display(self, obj):
        color = '#4CAF50' if obj.quantity_changed > 0 else '#f44336'
        sign = '+' if obj.quantity_changed > 0 else ''
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}{}</span>',
            color,
            sign,
            obj.quantity_changed
        )
    quantity_display.short_description = 'Quantity Changed'


@admin.register(SalesTransaction)
class SalesTransactionAdmin(admin.ModelAdmin):
    list_display = ('product', 'agent', 'quantity_display', 'amount_display', 'transaction_date')
    list_filter = ('transaction_date', 'agent')
    search_fields = ('product__title', 'agent__username')
    readonly_fields = ('created_at',)
    list_per_page = 25
    date_hierarchy = 'transaction_date'

    def quantity_display(self, obj):
        return format_html(
            '<span style="background: #2196F3; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;">{} units</span>',
            obj.quantity
        )
    quantity_display.short_description = 'Quantity'

    def amount_display(self, obj):
        return format_html('<span style="color: #2e7d32; font-weight: bold;">₹{}</span>', f'{obj.total_amount:.2f}')
    amount_display.short_description = 'Total Amount'


@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ('product', 'agent', 'threshold_display', 'active_badge', 'triggered_badge')
    list_filter = ('is_active', 'created_at')
    search_fields = ('product__title', 'agent__username')
    list_per_page = 25

    def threshold_display(self, obj):
        return format_html(
            '<span style="background: #FF9800; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;">Threshold: {}</span>',
            obj.threshold_quantity
        )
    threshold_display.short_description = 'Threshold'

    def active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #4CAF50; font-weight: bold;">● Active</span>')
        return format_html('<span style="color: #999;">● Inactive</span>')
    active_badge.short_description = 'Active'

    def triggered_badge(self, obj):
        if obj.is_triggered:
            return format_html('<span style="color: #f44336; font-weight: bold;">⚠ Triggered</span>')
        return format_html('<span style="color: #4CAF50; font-weight: bold;">✓ Normal</span>')
    triggered_badge.short_description = 'Status'


@admin.register(MarketDemandSuggestion)
class MarketDemandSuggestionAdmin(admin.ModelAdmin):
    list_display = ('product', 'agent', 'suggestion_type_badge', 'confidence_display', 'actioned_badge')
    list_filter = ('suggestion_type', 'is_actioned', 'created_at')
    search_fields = ('product__title', 'agent__username')
    readonly_fields = ('created_at',)
    list_per_page = 25
    date_hierarchy = 'created_at'

    def suggestion_type_badge(self, obj):
        colors = {'increase_stock': '#4CAF50', 'decrease_stock': '#f44336', 'discontinue': '#FF9800'}
        color = colors.get(obj.suggestion_type, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_suggestion_type_display()
        )
    suggestion_type_badge.short_description = 'Type'

    def confidence_display(self, obj):
        return format_html(
            '<span style="background: #2196F3; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;">{:.0f}%</span>',
            obj.confidence_score
        )
    confidence_display.short_description = 'Confidence'

    def actioned_badge(self, obj):
        if obj.is_actioned:
            return format_html('<span style="color: #4CAF50; font-weight: bold;">✓ Actioned</span>')
        return format_html('<span style="color: #FF9800; font-weight: bold;">⧖ Pending</span>')
    actioned_badge.short_description = 'Status'


class VehicleInline(admin.TabularInline):
    """Inline admin for Vehicle model"""
    model = Vehicle
    extra = 1
    fields = ('vehicle_type', 'vehicle_number', 'model', 'capacity', 'status', 'insured', 'insurance_expiry')
    list_per_page = 10


@admin.register(DeliveryPartner)
class DeliveryPartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_name', 'phone', 'status_badge', 'rating_display', 'rate_display', 'vehicle_count')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'contact_name', 'phone', 'email')
    readonly_fields = ('created_at', 'updated_at', 'total_deliveries')
    list_per_page = 25
    date_hierarchy = 'created_at'
    inlines = [VehicleInline]
    
    fieldsets = (
        ('Partner Information', {
            'fields': ('name', 'contact_name', 'phone', 'email', 'status')
        }),
        ('Location & Performance', {
            'fields': ('current_location', 'avg_delivery_time_hours', 'success_delivery_rate', 'total_deliveries')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def vehicle_count(self, obj):
        count = obj.vehicles.count()
        return format_html(
            '<span style="background-color: #2196F3; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{} vehicle{}</span>',
            count,
            's' if count != 1 else ''
        )
    vehicle_count.short_description = 'Vehicles'

    def status_badge(self, obj):
        colors = {'active': '#4CAF50', 'inactive': '#999', 'on_leave': '#FF9800'}
        color = colors.get(obj.status, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def rating_display(self, obj):
        return format_html('<span style="color: #FF9800; font-weight: bold;">★ {}</span>', f'{obj.avg_delivery_time_hours:.1f}')
    rating_display.short_description = 'Avg Time (hrs)'

    def rate_display(self, obj):
        rate = obj.success_delivery_rate
        return format_html(
            '<span style="color: #4CAF50; font-weight: bold;">{}%</span>',
            f'{rate:.0f}'
        )
    rate_display.short_description = 'Success Rate'


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('vehicle_number', 'vehicle_type_display', 'delivery_partner', 'status_badge', 'capacity', 'insurance_status')
    list_filter = ('vehicle_type', 'status', 'insured', 'delivery_partner')
    search_fields = ('vehicle_number', 'registration_number', 'model', 'delivery_partner__name')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Vehicle Details', {
            'fields': ('delivery_partner', 'vehicle_type', 'vehicle_number', 'model', 'capacity')
        }),
        ('Registration & Insurance', {
            'fields': ('registration_number', 'insured', 'insurance_expiry')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def vehicle_type_display(self, obj):
        colors = {'bike': '#2196F3', 'auto': '#4CAF50', 'car': '#FF9800', 'truck': '#9C27B0', 'van': '#00BCD4'}
        color = colors.get(obj.vehicle_type, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_vehicle_type_display()
        )
    vehicle_type_display.short_description = 'Type'
    
    def status_badge(self, obj):
        colors = {'active': '#4CAF50', 'maintenance': '#FF9800', 'inactive': '#999'}
        color = colors.get(obj.status, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def insurance_status(self, obj):
        if obj.insured:
            if obj.insurance_expiry:
                from django.utils import timezone
                if obj.insurance_expiry >= timezone.now().date():
                    return format_html('<span style="color: #4CAF50; font-weight: bold;">✓ Active</span>')
                else:
                    return format_html('<span style="color: #f44336; font-weight: bold;">✗ Expired</span>')
            return format_html('<span style="color: #4CAF50; font-weight: bold;">✓ Insured</span>')
        return format_html('<span style="color: #999;">Not Insured</span>')
    insurance_status.short_description = 'Insurance'


@admin.register(OrderDelivery)
class OrderDeliveryAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'agent', 'delivery_partner', 'vehicle_display', 'status_badge', 'assigned_at')
    list_filter = ('delivery_status', 'assigned_at', 'delivery_partner')
    search_fields = ('order__id', 'agent__username', 'delivery_partner__name', 'vehicle__vehicle_number')
    readonly_fields = ('created_at', 'updated_at', 'estimated_delivery_display')
    list_per_page = 25
    date_hierarchy = 'assigned_at'
    
    fieldsets = (
        ('Order & Agent', {
            'fields': ('order', 'agent')
        }),
        ('Delivery Assignment', {
            'fields': ('delivery_partner', 'vehicle', 'delivery_status', 'assigned_at')
        }),
        ('Delivery Progress', {
            'fields': ('picked_up_at', 'estimated_delivery_display', 'actual_delivery', 'last_location')
        }),
        ('Notes & Reasons', {
            'fields': ('delivery_notes', 'failed_reason'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def order_id(self, obj):
        return format_html('<span style="font-weight: bold; color: #2e7d32;">#{}</span>', obj.order.id)
    order_id.short_description = 'Order'
    
    def vehicle_display(self, obj):
        if obj.vehicle:
            return format_html(
                '<span style="background-color: #2196F3; color: white; padding: 3px 8px; border-radius: 3px;">{} ({})</span>',
                obj.vehicle.vehicle_number,
                obj.vehicle.get_vehicle_type_display()
            )
        return '—'
    vehicle_display.short_description = 'Vehicle'
    
    def estimated_delivery_display(self, obj):
        if obj.estimated_delivery:
            return obj.estimated_delivery
        elif obj.delivery_partner:
            estimated = obj.get_estimated_delivery()
            return estimated if estimated else '—'
        return '—'
    estimated_delivery_display.short_description = 'Estimated Delivery'

    def status_badge(self, obj):
        colors = {
            'not_assigned': '#999',
            'assigned': '#2196F3',
            'picked_up': '#2196F3',
            'in_transit': '#FF9800',
            'out_for_delivery': '#00BCD4',
            'delivered': '#4CAF50',
            'delivery_failed': '#f44336',
            'cancelled': '#999',
        }
        color = colors.get(obj.delivery_status, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_delivery_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(DeliveryTracking)
class DeliveryTrackingAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'stage_badge', 'location', 'stage_timestamp')
    list_filter = ('stage', 'stage_timestamp')
    search_fields = ('order_delivery__order__id', 'location')
    readonly_fields = ('stage_timestamp',)
    list_per_page = 25
    date_hierarchy = 'stage_timestamp'

    def order_id(self, obj):
        return format_html('<span style="font-weight: bold; color: #2e7d32;">#{}</span>', obj.order_delivery.order.id)
    order_id.short_description = 'Order'

    def stage_badge(self, obj):
        colors = {
            'confirmed': '#2196F3',
            'picked_up': '#FF9800',
            'in_transit': '#9C27B0',
            'out_for_delivery': '#FF5722',
            'delivered': '#4CAF50',
        }
        color = colors.get(obj.stage, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_stage_display()
        )
    stage_badge.short_description = 'Stage'


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'return_reason_badge', 'status_badge', 'requested_at', 'approved_by')
    list_filter = ('status', 'return_reason', 'requested_at')
    search_fields = ('order_item__order__id', 'return_description')
    readonly_fields = ('requested_at', 'created_at', 'updated_at')
    list_per_page = 25
    date_hierarchy = 'requested_at'

    def order_id(self, obj):
        return format_html('<span style="font-weight: bold; color: #2e7d32;">#{}</span>', obj.order_item.order.id)
    order_id.short_description = 'Order'

    def return_reason_badge(self, obj):
        colors = {
            'defective': '#f44336',
            'not_as_described': '#FF9800',
            'changed_mind': '#2196F3',
            'damaged': '#f44336',
        }
        color = colors.get(obj.return_reason, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_return_reason_display()
        )
    return_reason_badge.short_description = 'Reason'

    def status_badge(self, obj):
        colors = {
            'requested': '#FF9800',
            'approved': '#4CAF50',
            'rejected': '#f44336',
            'refunded': '#2196F3',
        }
        color = colors.get(obj.status, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'