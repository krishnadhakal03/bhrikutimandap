from django.urls import path
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('seller/<int:seller_id>/', views.seller_storefront, name='seller_storefront'),
    path('product/<int:product_id>/buy-now/', views.buy_now, name='buy_now'),
    path('product/<int:product_id>/chat/start/', views.start_seller_chat, name='start_seller_chat'),
    path('chat/<int:conversation_id>/messages/', views.seller_chat_messages, name='seller_chat_messages'),
    path('chat/<int:conversation_id>/send/', views.seller_chat_send, name='seller_chat_send'),
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('api/cart/add/', views.api_cart_add, name='api_cart_add'),
    path('api/cart/update/', views.api_cart_update, name='api_cart_update'),
    path('api/cart/remove/', views.api_cart_remove, name='api_cart_remove'),
    path('api/cart/', views.api_cart_detail, name='api_cart_detail'),
    path('api/payment-gateways/', views.api_payment_gateways, name='api_payment_gateways'),
    path('api/payments/create/', views.api_payments_create, name='api_payments_create'),
    path('api/payments/verify/', views.api_payments_verify, name='api_payments_verify'),
    path('api/chat/unread-counts/', views.chat_unread_counts_api, name='chat_unread_counts_api'),
    path('api/support-chat/', views.support_chat_api, name='support_chat_api'),
    path('api/payments/webhook/<str:gateway>/', views.payment_webhook, name='payment_webhook'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/return/', views.payment_return, name='payment_return'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/register/', views.register_view, name='register'),
    path('accounts/verify-otp/', views.verify_otp, name='verify_otp'),
    path('accounts/resend-otp/', views.resend_otp, name='resend_otp'),
    path('accounts/activate/<uidb64>/<token>/', views.activate_view, name='activate'),
    # Password reset routes
    path('accounts/password-reset/', views.CustomPasswordResetView.as_view(
        template_name='store/password_reset.html',
        success_url=reverse_lazy('store:password_reset_done')
    ), name='password_reset'),
    path('accounts/password-reset/done/', PasswordResetDoneView.as_view(
        template_name='store/password_reset_done.html'
    ), name='password_reset_done'),
    path('accounts/password-reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='store/password_reset_confirm.html',
        success_url=reverse_lazy('store:password_reset_complete')
    ), name='password_reset_confirm'),
    path('accounts/password-reset/complete/', PasswordResetCompleteView.as_view(
        template_name='store/password_reset_complete.html'
    ), name='password_reset_complete'),
    path('contact/', views.contact_view, name='contact'),
    path('blog/', views.blog_view, name='blog'),
    path('blog/<slug:slug>/', views.blog_detail_view, name='blog_detail'),
    # Order management routes
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/item/<int:order_item_id>/return/', views.request_return, name='request_return'),
    path('accounts/toggle-role/', views.toggle_role, name='toggle_role'),
    
    # ========== Customer Profile Management Routes ==========
    # Dashboard
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    
    # Profile Management
    path('customer/profile/', views.profile_detail, name='profile_detail'),
    
    # Address Management
    path('customer/addresses/', views.address_list, name='address_list'),
    path('customer/address/add/', views.address_create, name='address_create'),
    path('customer/address/<int:address_id>/edit/', views.address_update, name='address_update'),
    path('customer/address/<int:address_id>/delete/', views.address_delete, name='address_delete'),
    path('customer/address/<int:address_id>/set-default/', views.address_set_default, name='address_set_default'),
    
    # Payment Methods
    path('customer/payment-methods/', views.payment_method_list, name='payment_method_list'),
    path('customer/payment-method/add/', views.payment_method_create, name='payment_method_create'),
    path('customer/payment-method/<int:method_id>/delete/', views.payment_method_delete, name='payment_method_delete'),
    path('customer/payment-method/<int:method_id>/set-default/', views.payment_method_set_default, name='payment_method_set_default'),
    
    # Order History
    path('customer/orders/', views.order_history, name='order_history'),

    # Customer messages
    path('customer/messages/', views.customer_messages, name='customer_messages'),
    path('customer/messages/<int:conversation_id>/', views.customer_messages, name='customer_messages_detail'),
    
    # Wishlist
    path('customer/wishlist/', views.wishlist_view, name='wishlist'),
    path('customer/wishlist/add/<int:product_id>/', views.wishlist_add, name='wishlist_add'),
    path('customer/wishlist/remove/<int:product_id>/', views.wishlist_remove, name='wishlist_remove'),
]

