"""
Agent/Supplier Portal Views
Full CRUD for products, stock management, sales tracking, and analytics
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count, F
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from functools import wraps
import json

from store.models import (
    User, Product, Order, OrderItem, StockHistory, SalesTransaction,
    StockAlert, AgentProfile, MarketDemandSuggestion,
    DeliveryPartner, OrderDelivery, DeliveryTracking, ReturnRequest
)
from store.forms import (
    AgentProfileForm, AgentProductForm, StockAdjustmentForm,
    SalesTransactionForm, SalesFilterForm, StockAlertForm
)
from store.services import generate_market_insights_for_agent, process_return_approval, get_agent_dashboard_kpis


def agent_required(view_func):
    """Decorator to require agent role"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'agent':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied. Agent access required.')
        return redirect('store:login')
    return wrapper


# ==================== DASHBOARD ====================

@login_required
@agent_required
def agent_dashboard(request):
    """
    Agent dashboard with KPIs and overview
    """
    agent = request.user
    
    # Get date range for analytics
    days_back = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days_back)
    
    # Get real-time KPIs
    kpis = get_agent_dashboard_kpis(agent)
    
    # Key metrics
    products = agent.products.all()
    sales = SalesTransaction.objects.filter(
        agent=agent,
        transaction_date__gte=start_date
    )
    
    total_revenue = sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_sales = sales.aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    # Top selling products
    top_products = products.annotate(
        total_quantity=Sum('sales_transactions__quantity'),
        total_revenue=Sum('sales_transactions__total_amount')
    ).order_by('-total_revenue')[:5]
    
    # Recent sales
    recent_sales = sales.select_related('product').order_by('-transaction_date')[:10]
    
    # Get or create agent profile
    agent_profile, created = AgentProfile.objects.get_or_create(user=agent)
    
    context = {
        'agent_profile': agent_profile,
        'kpis': kpis,
        'total_revenue': total_revenue,
        'total_sales': total_sales,
        'total_products': products.count(),
        'top_products': top_products,
        'recent_sales': recent_sales,
        'days_back': days_back,
    }
    
    return render(request, 'agent/dashboard.html', context)


# ==================== PROFILE MANAGEMENT ====================

@login_required
@agent_required
def agent_profile_detail(request):
    """View agent profile"""
    agent_profile, created = AgentProfile.objects.get_or_create(user=request.user)
    
    context = {
        'agent_profile': agent_profile,
        'user': request.user
    }
    return render(request, 'agent/profile_detail.html', context)


@login_required
@agent_required
def agent_profile_edit(request):
    """Edit agent profile"""
    agent_profile, created = AgentProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = AgentProfileForm(request.POST, request.FILES, instance=agent_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('agent:profile_detail')
    else:
        form = AgentProfileForm(instance=agent_profile)
    
    context = {'form': form}
    return render(request, 'agent/profile_form.html', context)


# ==================== PRODUCT MANAGEMENT ====================

@login_required
@agent_required
def agent_products_list(request):
    """List agent's products"""
    products = request.user.products.all().order_by('-created_at')
    
    # Search and filter
    search = request.GET.get('search', '')
    if search:
        products = products.filter(Q(title__icontains=search) | Q(description__icontains=search))
    
    # Price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if min_price:
        products = products.filter(price__gte=float(min_price))
    if max_price:
        products = products.filter(price__lte=float(max_price))
    
    # Stock status filter
    stock_filter = request.GET.get('stock_status')
    if stock_filter == 'low':
        products = products.filter(stock__lt=10)
    elif stock_filter == 'out':
        products = products.filter(stock=0)
    elif stock_filter == 'in':
        products = products.filter(stock__gt=0)
    
    context = {
        'products': products,
        'search': search,
        'count': products.count()
    }
    return render(request, 'agent/products_list.html', context)


@login_required
@agent_required
def agent_product_create(request):
    """Create new product"""
    if request.method == 'POST':
        form = AgentProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.supplier = request.user
            product.save()
            messages.success(request, 'Product created successfully!')
            return redirect('agent:products_list')
    else:
        form = AgentProductForm()
    
    context = {'form': form, 'title': 'Add New Product'}
    return render(request, 'agent/product_form.html', context)


@login_required
@agent_required
def agent_product_edit(request, product_id):
    """Edit product"""
    product = get_object_or_404(Product, pk=product_id, supplier=request.user)
    
    if request.method == 'POST':
        form = AgentProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('agent:products_list')
    else:
        form = AgentProductForm(instance=product)
    
    context = {'form': form, 'product': product, 'title': 'Edit Product'}
    return render(request, 'agent/product_form.html', context)


@login_required
@agent_required
def agent_product_delete(request, product_id):
    """Delete product"""
    product = get_object_or_404(Product, pk=product_id, supplier=request.user)
    
    if request.method == 'POST':
        product_name = product.title
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('agent:products_list')
    
    context = {'product': product}
    return render(request, 'agent/product_confirm_delete.html', context)


# ==================== STOCK MANAGEMENT ====================

@login_required
@agent_required
def agent_stock_overview(request):
    """View stock overview"""
    products = request.user.products.all().annotate(
        total_sold=Sum('sales_transactions__quantity')
    ).order_by('-stock')
    
    # Low stock products
    low_stock = products.filter(stock__lt=10)
    
    # Stock history
    stock_history = StockHistory.objects.filter(
        product__supplier=request.user
    ).select_related('product').order_by('-created_at')[:20]
    
    context = {
        'products': products,
        'low_stock_count': low_stock.count(),
        'total_products': products.count(),
        'stock_history': stock_history
    }
    return render(request, 'agent/stock_overview.html', context)


@login_required
@agent_required
def agent_stock_adjust(request, product_id):
    """Adjust stock for a product"""
    product = get_object_or_404(Product, pk=product_id, supplier=request.user)
    
    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            old_stock = product.stock
            action = form.cleaned_data['action']
            quantity = form.cleaned_data['quantity_changed']
            reason = form.cleaned_data['reason']
            
            # Prevent negative stock
            if action == 'decrease' and (product.stock - quantity) < 0:
                messages.error(request, 'Cannot reduce stock below zero!')
                return redirect('agent:stock_adjust', product_id=product_id)
            
            # Update stock
            if action == 'increase':
                product.stock += quantity
            elif action in ['decrease', 'damage', 'return']:
                product.stock -= quantity
            
            # Handle adjustment action
            if action == 'adjustment':
                quantity_changed = quantity - old_stock
                product.stock = quantity
            else:
                quantity_changed = quantity if action == 'increase' else -quantity
            
            product.save()
            
            # Record history
            StockHistory.objects.create(
                product=product,
                agent=request.user,
                action=action,
                quantity_changed=quantity_changed,
                old_quantity=old_stock,
                new_quantity=product.stock,
                reason=reason
            )
            
            messages.success(request, 'Stock adjusted successfully!')
            return redirect('agent:stock_overview')
    else:
        form = StockAdjustmentForm()
    
    context = {'form': form, 'product': product}
    return render(request, 'agent/stock_adjust_form.html', context)


@login_required
@agent_required
def agent_stock_alerts(request):
    """Manage stock alerts"""
    alerts = StockAlert.objects.filter(agent=request.user).select_related('product')
    
    # Check which alerts are triggered
    triggered = []
    for alert in alerts:
        if alert.is_triggered():
            triggered.append(alert)
    
    context = {
        'alerts': alerts,
        'triggered_count': len(triggered)
    }
    return render(request, 'agent/stock_alerts.html', context)


@login_required
@agent_required
def agent_stock_alert_create(request, product_id):
    """Create stock alert for product"""
    product = get_object_or_404(Product, pk=product_id, supplier=request.user)
    
    if request.method == 'POST':
        form = StockAlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.agent = request.user
            alert.save()
            messages.success(request, 'Stock alert created!')
            return redirect('agent:stock_alerts')
    else:
        form = StockAlertForm(initial={'product': product})
    
    context = {'form': form, 'product': product}
    return render(request, 'agent/stock_alert_form.html', context)


# ==================== SALES MANAGEMENT ====================

@login_required
@agent_required
def agent_sales_list(request):
    """View sales transactions"""
    sales = SalesTransaction.objects.filter(
        agent=request.user
    ).select_related('product', 'order').order_by('-transaction_date')
    
    # Apply filters
    form = SalesFilterForm(request.GET)
    
    if form.is_valid():
        date_range = form.cleaned_data.get('date_range')
        product = form.cleaned_data.get('product')
        search = form.cleaned_data.get('search')
        
        if date_range == 'today':
            sales = sales.filter(transaction_date__date=timezone.now().date())
        elif date_range == '7days':
            sales = sales.filter(transaction_date__gte=timezone.now()-timedelta(days=7))
        elif date_range == '30days':
            sales = sales.filter(transaction_date__gte=timezone.now()-timedelta(days=30))
        elif date_range == '90days':
            sales = sales.filter(transaction_date__gte=timezone.now()-timedelta(days=90))
        
        if product:
            sales = sales.filter(product=product)
        
        if search:
            sales = sales.filter(product__title__icontains=search)
    
    # Paginate
    page = request.GET.get('page', 1)
    items_per_page = 20
    start = (int(page) - 1) * items_per_page
    end = start + items_per_page
    
    total_sales = sales.count()
    sales_page = sales[start:end]
    total_pages = (total_sales + items_per_page - 1) // items_per_page
    
    # Summary stats
    summary = sales.aggregate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('total_amount')
    )
    
    context = {
        'sales': sales_page,
        'form': form,
        'summary': summary,
        'page': page,
        'total_pages': total_pages,
        'total_count': total_sales
    }
    return render(request, 'agent/sales_list.html', context)


@login_required
@agent_required
def agent_sales_create(request):
    """Record a sales transaction"""
    # Limit to agent's products
    agent_products = request.user.products.all()
    
    if request.method == 'POST':
        form = SalesTransactionForm(request.POST)
        if form.is_valid():
            # Verify product belongs to agent
            product = form.cleaned_data['product']
            if product.supplier != request.user:
                messages.error(request, 'Invalid product!')
                return redirect('agent:sales_create')
            
            sale = form.save(commit=False)
            sale.agent = request.user
            sale.save()
            
            messages.success(request, 'Sale recorded successfully!')
            return redirect('agent:sales_list')
    else:
        form = SalesTransactionForm()
        form.fields['product'].queryset = agent_products
    
    context = {'form': form}
    return render(request, 'agent/sales_form.html', context)


# ==================== REPORTS & ANALYTICS ====================

@login_required
@agent_required
def agent_reports_dashboard(request):
    """
    Comprehensive reports dashboard
    """
    agent = request.user
    days_back = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days_back)
    
    # Sales summary
    sales = SalesTransaction.objects.filter(
        agent=agent,
        transaction_date__gte=start_date
    )
    
    total_revenue = sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_quantity = sales.aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    # Revenue by product
    revenue_by_product = agent.products.annotate(
        total_revenue=Sum('sales_transactions__total_amount'),
        total_quantity=Sum('sales_transactions__quantity')
    ).filter(total_revenue__isnull=False).order_by('-total_revenue')[:10]
    
    # Daily sales trend
    daily_sales = sales.values('transaction_date__date').annotate(
        revenue=Sum('total_amount'),
        quantity=Sum('quantity')
    ).order_by('transaction_date__date')
    
    context = {
        'total_revenue': total_revenue,
        'total_quantity': total_quantity,
        'revenue_by_product': revenue_by_product,
        'daily_sales': list(daily_sales),
        'days_back': days_back,
        'sales_count': sales.count()
    }
    return render(request, 'agent/reports.html', context)


# ==================== MARKET DEMAND INSIGHTS ====================

@login_required
@agent_required
def agent_market_insights(request):
    """
    AI-driven market demand insights
    """
    agent = request.user
    
    # Generate fresh insights
    days_back = int(request.GET.get('days', 30))
    suggestions = generate_market_insights_for_agent(agent, days_back=days_back)
    
    # Get saved suggestions
    saved_suggestions = MarketDemandSuggestion.objects.filter(
        agent=agent
    ).order_by('-confidence_score')
    
    # Group by type
    trending = saved_suggestions.filter(suggestion_type='trending')
    declining = saved_suggestions.filter(suggestion_type='declining')
    seasonal = saved_suggestions.filter(suggestion_type='seasonal')
    
    context = {
        'trending': trending,
        'declining': declining,
        'seasonal': seasonal,
        'all_suggestions': saved_suggestions,
        'days_back': days_back
    }
    return render(request, 'agent/market_insights.html', context)


# ==================== ORDER MANAGEMENT ====================

@login_required
@agent_required
def agent_orders(request):
    """
    View customer orders for agent's products
    """
    # Orders containing agent's products
    orders = Order.objects.filter(
        items__product__supplier=request.user
    ).distinct().select_related('user').prefetch_related('items').order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    context = {
        'orders': orders,
        'status_filter': status
    }
    return render(request, 'agent/orders.html', context)


@login_required
@agent_required
def agent_order_detail(request, order_id):
    """
    View detailed order information
    """
    order = get_object_or_404(Order, pk=order_id)
    
    # Verify agent has items in this order
    agent_items = order.items.filter(product__supplier=request.user)
    if not agent_items.exists():
        messages.error(request, 'Access denied!')
        return redirect('agent:orders')
    
    context = {
        'order': order,
        'agent_items': agent_items
    }
    return render(request, 'agent/order_detail.html', context)


@login_required
@agent_required
def agent_order_status_update(request, order_id):
    """
    Update order status/delivery status
    """
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=order_id)
        
        # Verify permission
        agent_items = order.items.filter(product__supplier=request.user)
        if not agent_items.exists():
            return JsonResponse({'ok': False, 'error': 'Access denied'})
        
        data = json.loads(request.body)
        new_status = data.get('status')
        
        if new_status in ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']:
            order.status = new_status
            order.save()
            
            return JsonResponse({
                'ok': True,
                'message': f'Order status updated to {new_status}'
            })
        
        return JsonResponse({'ok': False, 'error': 'Invalid status'})
    
    return JsonResponse({'ok': False, 'error': 'Invalid request'})

# ==================== DELIVERY MANAGEMENT ====================

@login_required
@agent_required
def agent_incoming_orders(request):
    """
    Dashboard showing all incoming orders for agent's products
    """
    # Orders with agent's products that haven't been assigned to delivery
    from store.models import OrderDelivery
    
    agent = request.user
    
    # Get all orders with agent's items
    orders_with_agent_items = Order.objects.filter(
        items__product__supplier=agent
    ).distinct().select_related('user', 'delivery_address').prefetch_related('items', 'delivery')
    
    # Separate by delivery status
    new_orders = []
    assigned_orders = []
    in_transit_orders = []
    delivered_orders = []
    
    for order in orders_with_agent_items:
        try:
            delivery = order.delivery
            if delivery.delivery_status == 'not_assigned':
                new_orders.append(order)
            elif delivery.delivery_status in ['assigned', 'picked_up']:
                assigned_orders.append(order)
            elif delivery.delivery_status in ['in_transit', 'out_for_delivery']:
                in_transit_orders.append(order)
            elif delivery.delivery_status == 'delivered':
                delivered_orders.append(order)
        except OrderDelivery.DoesNotExist:
            # Create delivery record if doesn't exist
            OrderDelivery.objects.create(
                order=order,
                agent=agent,
                delivery_status='not_assigned'
            )
            new_orders.append(order)
    
    context = {
        'new_orders': new_orders,
        'assigned_orders': assigned_orders,
        'in_transit_orders': in_transit_orders,
        'delivered_orders': delivered_orders,
        'total_new': len(new_orders),
        'total_assigned': len(assigned_orders),
        'total_in_transit': len(in_transit_orders),
        'total_delivered': len(delivered_orders),
    }
    return render(request, 'agent/incoming_orders.html', context)


@login_required
@agent_required
def agent_assign_delivery(request, order_id):
    """
    Assign delivery partner and vehicle to an order
    """
    from store.models import OrderDelivery, DeliveryPartner, Vehicle
    
    order = get_object_or_404(Order, pk=order_id)
    
    # Verify agent has items in this order
    agent_items = order.items.filter(product__supplier=request.user)
    if not agent_items.exists():
        messages.error(request, 'Access denied')
        return redirect('agent:incoming_orders')
    
    # Get or create order delivery
    order_delivery, created = OrderDelivery.objects.get_or_create(
        order=order,
        defaults={'agent': request.user, 'delivery_status': 'not_assigned'}
    )
    
    if request.method == 'POST':
        delivery_partner_id = request.POST.get('delivery_partner_id')
        vehicle_id = request.POST.get('vehicle_id')
        
        if not delivery_partner_id:
            messages.error(request, 'Please select a delivery partner')
            return redirect('agent:assign_delivery', order_id=order_id)
        
        try:
            delivery_partner = DeliveryPartner.objects.get(pk=delivery_partner_id, status='active')
            vehicle = None
            
            # Get selected vehicle if provided
            if vehicle_id:
                vehicle = Vehicle.objects.get(pk=vehicle_id, delivery_partner=delivery_partner, status='active')
            else:
                # Get first available vehicle for this partner
                vehicle = delivery_partner.vehicles.filter(status='active').first()
            
            # Assign delivery
            order_delivery.delivery_partner = delivery_partner
            order_delivery.vehicle = vehicle
            order_delivery.delivery_status = 'assigned'
            order_delivery.assigned_at = timezone.now()
            order_delivery.estimated_delivery = order_delivery.get_estimated_delivery()
            order_delivery.save()
            
            # Create tracking stage
            vehicle_info = f" using {vehicle.vehicle_number}" if vehicle else ""
            DeliveryTracking.objects.create(
                order_delivery=order_delivery,
                stage='order_confirmed',
                location='Order confirmed and ready for pickup',
                notes=f'Assigned to {delivery_partner.name}{vehicle_info}'
            )
            
            messages.success(request, f'Order assigned to {delivery_partner.name}{vehicle_info}')
            return redirect('agent:delivery_tracking', order_id=order_id)
        
        except DeliveryPartner.DoesNotExist:
            messages.error(request, 'Invalid delivery partner selected')
    
    # Get available delivery partners
    delivery_partners = DeliveryPartner.objects.filter(status='active').order_by('success_delivery_rate')
    
    context = {
        'order': order,
        'order_delivery': order_delivery,
        'delivery_partners': delivery_partners,
        'agent_items': agent_items
    }
    return render(request, 'agent/assign_delivery.html', context)


@login_required
@agent_required
def agent_delivery_tracking(request, order_id):
    """
    Pizza trajectory - show delivery stages and progress
    """
    from store.models import OrderDelivery, DeliveryTracking
    
    order = get_object_or_404(Order, pk=order_id)
    
    try:
        order_delivery = order.delivery
    except OrderDelivery.DoesNotExist:
        messages.error(request, 'Delivery not found')
        return redirect('agent:incoming_orders')
    
    # Get tracking history
    tracking_stages = DeliveryTracking.objects.filter(
        order_delivery=order_delivery
    ).order_by('stage_timestamp')
    
    # Get current stage
    stage_sequence = [
        'order_confirmed',
        'packed',
        'picked_up',
        'in_transit',
        'out_for_delivery',
        'delivered'
    ]
    
    current_stage_index = 0
    for i, stage in enumerate(stage_sequence):
        if tracking_stages.filter(stage=stage).exists():
            current_stage_index = i
    
    progress_percentage = (current_stage_index / len(stage_sequence)) * 100
    
    context = {
        'order': order,
        'order_delivery': order_delivery,
        'tracking_stages': tracking_stages,
        'delivery_partner': order_delivery.delivery_partner,
        'stage_sequence': stage_sequence,
        'current_stage_index': current_stage_index,
        'progress_percentage': progress_percentage,
    }
    return render(request, 'agent/delivery_tracking.html', context)


@login_required
@agent_required
def agent_update_delivery_status(request, order_id):
    """
    AJAX endpoint to update delivery status and add tracking stage
    """
    from store.models import OrderDelivery, DeliveryTracking
    
    order = get_object_or_404(Order, pk=order_id)
    
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Invalid request'})
    
    try:
        order_delivery = order.delivery
    except OrderDelivery.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Delivery not found'})
    
    # Verify permission
    if order_delivery.agent != request.user:
        return JsonResponse({'ok': False, 'error': 'Access denied'})
    
    try:
        data = json.loads(request.body)
        new_stage = data.get('stage')
        location = data.get('location', '')
        notes = data.get('notes', '')
        
        # Add tracking stage
        DeliveryTracking.objects.create(
            order_delivery=order_delivery,
            stage=new_stage,
            location=location,
            notes=notes
        )
        
        # Update delivery status
        stage_to_status = {
            'order_confirmed': 'assigned',
            'packed': 'assigned',
            'picked_up': 'picked_up',
            'in_transit': 'in_transit',
            'out_for_delivery': 'out_for_delivery',
            'delivered': 'delivered',
        }
        
        order_delivery.delivery_status = stage_to_status.get(new_stage, order_delivery.delivery_status)
        order_delivery.last_location = location
        order_delivery.save()
        
        # Update order status
        if new_stage == 'delivered':
            order_delivery.mark_as_delivered()
        
        return JsonResponse({
            'ok': True,
            'message': f'Delivery updated to {new_stage.replace("_", " ").title()}'
        })
    
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@login_required
@agent_required
def agent_handle_return(request, order_id, item_id):
    """
    Handle product return request
    """
    from store.models import OrderDelivery, ReturnRequest
    
    order = get_object_or_404(Order, pk=order_id)
    order_item = get_object_or_404(OrderItem, pk=item_id, order=order)
    
    # Verify agent has this item
    if order_item.product.supplier != request.user:
        messages.error(request, 'Access denied')
        return redirect('agent:order_detail', order_id=order_id)
    
    try:
        return_request = order_item.return_request
    except ReturnRequest.DoesNotExist:
        messages.error(request, 'No return request found')
        return redirect('agent:order_detail', order_id=order_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        refund_amount = request.POST.get('refund_amount', 0)
        
        if action == 'approve':
            return_request.refund_amount = float(refund_amount) or order_item.total_price()
            return_request.save()
            
            # Process return approval: restores stock and updates return status
            if process_return_approval(return_request):
                messages.success(request, 'Return approved!')
            else:
                messages.error(request, 'Error processing return approval')
        
        elif action == 'reject':
            return_request.status = 'rejected'
            return_request.agent_notes = notes
            return_request.approved_by = request.user
            return_request.approved_at = timezone.now()
            return_request.save()
            messages.success(request, 'Return rejected!')
        
        return redirect('agent:order_detail', order_id=order_id)
    
    context = {
        'return_request': return_request,
        'order_item': order_item,
        'order': order
    }
    return render(request, 'agent/handle_return.html', context)


# ==================== DELIVERY PARTNER MANAGEMENT ====================

@login_required
@agent_required
def agent_delivery_partners(request):
    """
    List agent's configured delivery partners
    """
    from store.models import AgentDeliveryPartner
    
    agent_profile = AgentProfile.objects.get(user=request.user)
    delivery_partnerships = AgentDeliveryPartner.objects.filter(agent=agent_profile)
    available_partners = DeliveryPartner.objects.filter(status='active')
    
    # Get partners already configured
    configured_partner_ids = delivery_partnerships.values_list('delivery_partner_id', flat=True)
    available_to_add = available_partners.exclude(id__in=configured_partner_ids)
    
    context = {
        'delivery_partnerships': delivery_partnerships,
        'available_partners': available_to_add,
        'agent_profile': agent_profile
    }
    return render(request, 'agent/delivery_partners.html', context)


@login_required
@agent_required
def agent_add_delivery_partner(request):
    """
    Add a delivery partner to agent's configuration
    """
    from store.models import AgentDeliveryPartner
    from store.forms import AgentDeliveryPartnerForm
    
    agent_profile = AgentProfile.objects.get(user=request.user)
    
    if request.method == 'POST':
        form = AgentDeliveryPartnerForm(request.POST)
        if form.is_valid():
            partnership = form.save(commit=False)
            partnership.agent = agent_profile
            
            # Check if partnership already exists
            existing = AgentDeliveryPartner.objects.filter(
                agent=agent_profile,
                delivery_partner=partnership.delivery_partner
            ).first()
            
            if existing:
                messages.warning(request, 'This delivery partner is already configured.')
                return redirect('agent:delivery_partners')
            
            partnership.save()
            messages.success(request, f'Added {partnership.delivery_partner.name} as a delivery partner!')
            return redirect('agent:delivery_partners')
    else:
        form = AgentDeliveryPartnerForm()
        # Filter to show only available partners
        available_partners = DeliveryPartner.objects.filter(status='active')
        configured_ids = AgentDeliveryPartner.objects.filter(
            agent=agent_profile
        ).values_list('delivery_partner_id', flat=True)
        form.fields['delivery_partner'].queryset = available_partners.exclude(
            id__in=configured_ids
        )
    
    context = {
        'form': form,
        'agent_profile': agent_profile,
        'page_title': 'Add Delivery Partner'
    }
    return render(request, 'agent/add_delivery_partner.html', context)


@login_required
@agent_required
def agent_edit_delivery_partner(request, partner_id):
    """
    Edit delivery partner configuration
    """
    from store.models import AgentDeliveryPartner
    from store.forms import AgentDeliveryPartnerForm
    
    agent_profile = AgentProfile.objects.get(user=request.user)
    partnership = get_object_or_404(
        AgentDeliveryPartner,
        id=partner_id,
        agent=agent_profile
    )
    
    if request.method == 'POST':
        form = AgentDeliveryPartnerForm(request.POST, instance=partnership)
        if form.is_valid():
            form.save()
            messages.success(request, f'Updated {partnership.delivery_partner.name} configuration!')
            return redirect('agent:delivery_partners')
    else:
        form = AgentDeliveryPartnerForm(instance=partnership)
    
    context = {
        'form': form,
        'partnership': partnership,
        'agent_profile': agent_profile,
        'page_title': f'Edit {partnership.delivery_partner.name}'
    }
    return render(request, 'agent/edit_delivery_partner.html', context)


@login_required
@agent_required
def agent_remove_delivery_partner(request, partner_id):
    """
    Remove a delivery partner from agent's configuration
    """
    from store.models import AgentDeliveryPartner
    
    agent_profile = AgentProfile.objects.get(user=request.user)
    partnership = get_object_or_404(
        AgentDeliveryPartner,
        id=partner_id,
        agent=agent_profile
    )
    
    partner_name = partnership.delivery_partner.name
    partnership.delete()
    messages.success(request, f'Removed {partner_name} from your delivery partners.')
    return redirect('agent:delivery_partners')


@login_required
@agent_required
def agent_set_preferred_partner(request, partner_id):
    """
    Set a delivery partner as preferred (via AJAX or form post)
    """
    from store.models import AgentDeliveryPartner
    
    agent_profile = AgentProfile.objects.get(user=request.user)
    partnership = get_object_or_404(
        AgentDeliveryPartner,
        id=partner_id,
        agent=agent_profile
    )
    
    # Unset other preferred partners
    AgentDeliveryPartner.objects.filter(
        agent=agent_profile,
        is_preferred=True
    ).update(is_preferred=False)
    
    # Set this one as preferred
    partnership.is_preferred = True
    partnership.save()
    
    messages.success(request, f'{partnership.delivery_partner.name} is now your preferred delivery partner!')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'Preferred partner updated'})
    
    return redirect('agent:delivery_partners')
