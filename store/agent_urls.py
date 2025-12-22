"""
Agent/Supplier Portal URL Configuration
"""
from django.urls import path
from . import agent_views

app_name = 'agent'

urlpatterns = [
    # Dashboard
    path('dashboard/', agent_views.agent_dashboard, name='dashboard'),
    
    # Profile Management
    path('profile/', agent_views.agent_profile_detail, name='profile_detail'),
    path('profile/edit/', agent_views.agent_profile_edit, name='profile_edit'),
    
    # Product Management
    path('products/', agent_views.agent_products_list, name='products_list'),
    path('product/add/', agent_views.agent_product_create, name='product_create'),
    path('product/<int:product_id>/edit/', agent_views.agent_product_edit, name='product_edit'),
    path('product/<int:product_id>/delete/', agent_views.agent_product_delete, name='product_delete'),
    
    # Stock Management
    path('stock/', agent_views.agent_stock_overview, name='stock_overview'),
    path('stock/<int:product_id>/adjust/', agent_views.agent_stock_adjust, name='stock_adjust'),
    path('stock/alerts/', agent_views.agent_stock_alerts, name='stock_alerts'),
    path('stock/alert/<int:product_id>/add/', agent_views.agent_stock_alert_create, name='stock_alert_create'),
    
    # Sales Management
    path('sales/', agent_views.agent_sales_list, name='sales_list'),
    path('sales/record/', agent_views.agent_sales_create, name='sales_create'),
    
    # Reports & Analytics
    path('reports/', agent_views.agent_reports_dashboard, name='reports'),
    path('insights/', agent_views.agent_market_insights, name='market_insights'),
    
    # Order Management
    path('orders/', agent_views.agent_orders, name='orders'),
    path('orders/incoming/', agent_views.agent_incoming_orders, name='incoming_orders'),
    path('orders/<int:order_id>/', agent_views.agent_order_detail, name='order_detail'),
    path('orders/<int:order_id>/status/', agent_views.agent_order_status_update, name='order_status_update'),
    
    # Delivery Management
    path('orders/<int:order_id>/assign-delivery/', agent_views.agent_assign_delivery, name='assign_delivery'),
    path('orders/<int:order_id>/tracking/', agent_views.agent_delivery_tracking, name='delivery_tracking'),
    path('orders/<int:order_id>/update-delivery/', agent_views.agent_update_delivery_status, name='update_delivery_status'),
    
    # Return Management
    path('orders/<int:order_id>/item/<int:item_id>/return/', agent_views.agent_handle_return, name='handle_return'),
    
    # Delivery Partner Management
    path('delivery-partners/', agent_views.agent_delivery_partners, name='delivery_partners'),
    path('delivery-partners/add/', agent_views.agent_add_delivery_partner, name='add_delivery_partner'),
    path('delivery-partners/<int:partner_id>/edit/', agent_views.agent_edit_delivery_partner, name='edit_delivery_partner'),
    path('delivery-partners/<int:partner_id>/remove/', agent_views.agent_remove_delivery_partner, name='remove_delivery_partner'),
    path('delivery-partners/<int:partner_id>/set-preferred/', agent_views.agent_set_preferred_partner, name='set_preferred_partner'),
]