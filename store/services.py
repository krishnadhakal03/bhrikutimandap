"""
Market Demand Analysis Service - Agent Portal
Rule-based demand analysis with extension points for ML/LLM integration

Architecture:
- Service layer for business logic
- Pluggable analyzers for different analysis types
- Clearly marked extension points for future ML integration
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from store.models import SalesTransaction, Product, MarketDemandSuggestion
from django.db.models import Sum, Count, Q
import django.db.models


class MarketDemandAnalyzer:
    """
    Main service for analyzing market demand
    Coordinates different analysis strategies
    """
    
    def __init__(self, agent=None, days_back=30):
        self.agent = agent
        self.days_back = days_back
        self.cutoff_date = timezone.now() - timedelta(days=days_back)
        
    def analyze_all_products(self):
        """
        Analyze all products for the agent and generate suggestions
        """
        if not self.agent:
            return []
        
        products = self.agent.products.all()
        suggestions = []
        
        for product in products:
            product_suggestions = self._analyze_product(product)
            suggestions.extend(product_suggestions)
        
        return suggestions
    
    def _analyze_product(self, product):
        """
        Analyze a single product and return suggestions
        """
        suggestions = []
        
        # Get sales data for this product
        sales_data = self._get_sales_data(product)
        
        if not sales_data:
            return suggestions
        
        # Run different analyzers
        trending = TrendingProductAnalyzer().analyze(product, sales_data, self.days_back)
        if trending:
            suggestions.append(trending)
        
        declining = DecliningProductAnalyzer().analyze(product, sales_data, self.days_back)
        if declining:
            suggestions.append(declining)
        
        seasonal = SeasonalPatternAnalyzer().analyze(product, sales_data, self.days_back)
        if seasonal:
            suggestions.append(seasonal)
        
        return suggestions
    
    def _get_sales_data(self, product):
        """
        Get aggregated sales data for a product within date range
        
        Returns: {
            'total_quantity': int,
            'total_revenue': Decimal,
            'transaction_count': int,
            'avg_price': Decimal,
            'daily_sales': list,
            'weekly_sales': list,
        }
        """
        transactions = SalesTransaction.objects.filter(
            product=product,
            transaction_date__gte=self.cutoff_date
        )
        
        if not transactions.exists():
            return None
        
        aggregates = transactions.aggregate(
            total_qty=Sum('quantity'),
            total_revenue=Sum('total_amount'),
            count=Count('id'),
            avg_price=Sum('total_amount') / Count('id')
        )
        
        return {
            'total_quantity': aggregates['total_qty'] or 0,
            'total_revenue': aggregates['total_revenue'] or 0,
            'transaction_count': aggregates['count'],
            'avg_price': aggregates['avg_price'],
            'transactions': list(transactions)
        }
    
    def save_suggestion(self, suggestion_dict):
        """
        Save suggestion to database
        """
        MarketDemandSuggestion.objects.create(**suggestion_dict)


class TrendingProductAnalyzer:
    """
    Analyzer for trending/increasing demand products
    Rules:
    - 20%+ increase in weekly sales
    - OR increasing sale trend over last 4 weeks
    - OR top 25% by revenue
    """
    
    def analyze(self, product, sales_data, days_back):
        """
        Check if product is trending
        """
        if not sales_data:
            return None
        
        # RULE 1: Check growth trend
        growth_score = self._calculate_growth_trend(sales_data['transactions'], days_back)
        
        # RULE 2: Check if top performer
        percentile = self._calculate_percentile(product, sales_data)
        
        # RULE 3: Check velocity (sales per day)
        velocity = sales_data['total_quantity'] / (days_back + 1)
        
        confidence = 0.0
        reason = ""
        
        if growth_score > 0.2:  # 20% growth
            confidence = min(1.0, growth_score)
            reason = f"Sales showing {growth_score*100:.0f}% growth trend"
        
        if percentile >= 75:  # Top 25%
            confidence = max(confidence, 0.8)
            reason += f" | Top performer (75th percentile)"
        
        if velocity > 5:  # More than 5 units per day
            confidence = max(confidence, 0.6)
            reason += f" | High velocity ({velocity:.1f} units/day)"
        
        if confidence > 0.5:
            return {
                'suggestion_type': 'trending',
                'confidence_score': confidence,
                'reason': reason.strip(' |'),
                'data_period': self._get_period_key(days_back),
                'product': product,
                'agent': product.supplier
            }
        
        return None
    
    def _calculate_growth_trend(self, transactions, days_back):
        """
        Calculate growth trend by comparing first half vs second half
        """
        if len(transactions) < 2:
            return 0.0
        
        mid_point = len(transactions) // 2
        first_half = sum(t.quantity for t in transactions[:mid_point])
        second_half = sum(t.quantity for t in transactions[mid_point:])
        
        if first_half == 0:
            return 0.0
        
        growth = (second_half - first_half) / first_half
        return max(0, growth)  # Only positive growth
    
    def _calculate_percentile(self, product, sales_data):
        """
        Calculate where this product ranks among all products
        """
        all_products_revenue = SalesTransaction.objects.filter(
            product__supplier=product.supplier
        ).values('product').annotate(
            total=Sum('total_amount')
        ).order_by('-total')
        
        if not all_products_revenue:
            return 50
        
        rank = 0
        for i, item in enumerate(all_products_revenue):
            if item['product'] == product.id:
                rank = i
                break
        
        percentile = (1 - (rank / len(all_products_revenue))) * 100
        return percentile
    
    def _get_period_key(self, days_back):
        """Convert days to period key"""
        if days_back <= 7:
            return '7_days'
        elif days_back <= 30:
            return '30_days'
        return '90_days'


class DecliningProductAnalyzer:
    """
    Analyzer for declining/decreasing demand products
    Rules:
    - 20% decrease in weekly sales
    - OR consistently low sales
    - OR zero sales for extended period
    """
    
    def analyze(self, product, sales_data, days_back):
        """
        Check if product is declining
        """
        if not sales_data:
            # No sales at all = declining
            if product.stock > 10:
                return {
                    'suggestion_type': 'declining',
                    'confidence_score': 0.7,
                    'reason': 'No sales recorded in this period despite adequate stock',
                    'data_period': self._get_period_key(days_back),
                    'product': product,
                    'agent': product.supplier
                }
            return None
        
        # RULE 1: Check decline trend
        decline_score = self._calculate_decline_trend(sales_data['transactions'], days_back)
        
        # RULE 2: Check if bottom performer
        percentile = self._calculate_percentile(product, sales_data)
        
        confidence = 0.0
        reason = ""
        
        if decline_score > 0.2:  # 20% decline
            confidence = min(1.0, decline_score)
            reason = f"Sales showing {decline_score*100:.0f}% decline trend"
        
        if percentile <= 25:  # Bottom 25%
            confidence = max(confidence, 0.7)
            reason += f" | Low performer (bottom 25%)"
        
        if confidence > 0.5:
            return {
                'suggestion_type': 'declining',
                'confidence_score': confidence,
                'reason': reason.strip(' |'),
                'data_period': self._get_period_key(days_back),
                'product': product,
                'agent': product.supplier
            }
        
        return None
    
    def _calculate_decline_trend(self, transactions, days_back):
        """
        Calculate decline trend by comparing first half vs second half
        """
        if len(transactions) < 2:
            return 0.0
        
        mid_point = len(transactions) // 2
        first_half = sum(t.quantity for t in transactions[:mid_point])
        second_half = sum(t.quantity for t in transactions[mid_point:])
        
        if first_half == 0:
            return 0.0
        
        decline = (first_half - second_half) / first_half
        return max(0, decline)  # Only positive decline
    
    def _calculate_percentile(self, product, sales_data):
        """
        Calculate where this product ranks among all products
        """
        all_products_revenue = SalesTransaction.objects.filter(
            product__supplier=product.supplier
        ).values('product').annotate(
            total=Sum('total_amount')
        ).order_by('-total')
        
        if not all_products_revenue:
            return 50
        
        rank = 0
        for i, item in enumerate(all_products_revenue):
            if item['product'] == product.id:
                rank = i
                break
        
        percentile = (1 - (rank / len(all_products_revenue))) * 100
        return percentile
    
    def _get_period_key(self, days_back):
        """Convert days to period key"""
        if days_back <= 7:
            return '7_days'
        elif days_back <= 30:
            return '30_days'
        return '90_days'


class SeasonalPatternAnalyzer:
    """
    Analyzer for seasonal patterns
    Rules:
    - Spike in sales during specific days/weeks
    - Could indicate seasonal demand
    """
    
    def analyze(self, product, sales_data, days_back):
        """
        Check for seasonal patterns
        """
        if not sales_data or len(sales_data['transactions']) < 5:
            return None
        
        # Simple heuristic: if sales vary significantly, might be seasonal
        daily_sales = self._calculate_daily_sales(sales_data['transactions'])
        
        if not daily_sales:
            return None
        
        std_dev = self._calculate_std_dev(daily_sales)
        avg = sum(daily_sales) / len(daily_sales)
        
        if avg > 0 and std_dev / avg > 0.5:  # High variance
            return {
                'suggestion_type': 'seasonal',
                'confidence_score': 0.5,
                'reason': f'Sales show seasonal variation (high variance pattern)',
                'data_period': self._get_period_key(days_back),
                'product': product,
                'agent': product.supplier
            }
        
        return None
    
    def _calculate_daily_sales(self, transactions):
        """Get daily sales amounts"""
        daily = {}
        for transaction in transactions:
            date = transaction.transaction_date.date()
            daily[date] = daily.get(date, 0) + transaction.quantity
        
        return list(daily.values())
    
    def _calculate_std_dev(self, values):
        """Simple standard deviation calculation"""
        if len(values) < 2:
            return 0.0
        
        avg = sum(values) / len(values)
        variance = sum((x - avg) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _get_period_key(self, days_back):
        """Convert days to period key"""
        if days_back <= 7:
            return '7_days'
        elif days_back <= 30:
            return '30_days'
        return '90_days'


# EXTENSION POINTS FOR FUTURE ML/LLM INTEGRATION:
# ================================================

class MLBasedDemandAnalyzer:
    """
    [FUTURE] ML-based demand analyzer
    Extension point for integrating machine learning models
    
    Usage:
    - Train on historical sales data
    - Predict future demand using regression/time-series models
    - Rank products by predicted demand change
    
    Implementation hints:
    - Use scikit-learn for regression models
    - Use Prophet for time-series forecasting
    - Use LSTM for deep learning predictions
    """
    
    def analyze(self, product, sales_data, days_back):
        """
        [NOT IMPLEMENTED]
        Analyze using ML models
        """
        # TODO: Implement ML-based analysis
        pass


class LLMBasedInsightGenerator:
    """
    [FUTURE] LLM-based insight generator
    Extension point for integrating Large Language Models
    
    Usage:
    - Feed sales data and trends to LLM
    - Get natural language insights and recommendations
    - Generate actionable business suggestions
    
    Implementation hints:
    - Use OpenAI API (GPT-3.5/GPT-4)
    - Use Google PaLM API
    - Use Hugging Face models
    - Use Anthropic Claude API
    
    Example prompt structure:
    "Given this sales data: [data], provide insights on:
     1. Product demand trends
     2. Recommended inventory levels
     3. Pricing strategy
     4. Marketing focus areas"
    """
    
    def generate_insights(self, product, sales_data, market_context):
        """
        [NOT IMPLEMENTED]
        Generate insights using LLM
        """
        # TODO: Implement LLM-based insights
        pass


def generate_market_insights_for_agent(agent, days_back=30):
    """
    Main entry point for generating market insights
    """
    analyzer = MarketDemandAnalyzer(agent=agent, days_back=days_back)
    suggestions = analyzer.analyze_all_products()
    
    # Clear old suggestions
    MarketDemandSuggestion.objects.filter(
        agent=agent,
        created_at__lte=timezone.now() - timedelta(days=1)
    ).delete()
    
    # Save new suggestions
    for suggestion_dict in suggestions:
        analyzer.save_suggestion(suggestion_dict)
    
    return suggestions


if __name__ == '__main__':
    print("Market Demand Analysis Service")
    print("=" * 80)
    print("\nService Architecture:")
    print("  - MarketDemandAnalyzer: Main coordinator")
    print("  - TrendingProductAnalyzer: Rule-based trending detection")
    print("  - DecliningProductAnalyzer: Rule-based decline detection")
    print("  - SeasonalPatternAnalyzer: Rule-based seasonal pattern detection")
    print("\nExtension Points (For Future Integration):")
    print("  - MLBasedDemandAnalyzer: ML/Statistical models")
    print("  - LLMBasedInsightGenerator: Large Language Model integration")
    print("\n" + "=" * 80)

# ==================== ORDER & STOCK MANAGEMENT ====================

def process_order_created(order):
    """
    Process newly created order:
    1. Reduce stock for each product
    2. Create order delivery record
    3. Log stock history
    """
    from django.db import transaction
    from store.models import OrderDelivery, StockHistory
    
    try:
        with transaction.atomic():
            for item in order.items.all():
                product = item.product
                old_stock = product.stock
                
                # Reduce stock
                if product.stock >= item.quantity:
                    product.stock -= item.quantity
                    product.save()
                    
                    # Log stock history
                    StockHistory.objects.create(
                        product=product,
                        agent=product.supplier,
                        action='decrease',
                        quantity_changed=item.quantity,
                        old_quantity=old_stock,
                        new_quantity=product.stock,
                        reason=f'Order #{order.id} placed'
                    )
                else:
                    raise ValueError(f'Insufficient stock for {product.title}')
            
            # Create order delivery record for each agent
            agents = set()
            for item in order.items.all():
                if item.product.supplier:
                    agents.add(item.product.supplier)
            
            for agent in agents:
                OrderDelivery.objects.get_or_create(
                    order=order,
                    defaults={
                        'agent': agent,
                        'delivery_status': 'not_assigned'
                    }
                )
            
            return True
    except Exception as e:
        print(f"Error processing order: {str(e)}")
        return False


def process_return_approval(return_request):
    """
    Handle approved return:
    1. Return stock to agent
    2. Process refund
    3. Update order item status
    """
    from django.db import transaction
    from store.models import StockHistory
    
    try:
        with transaction.atomic():
            order_item = return_request.order_item
            product = order_item.product
            old_stock = product.stock
            
            # Return stock
            product.stock += order_item.quantity
            product.save()
            
            # Log stock history
            StockHistory.objects.create(
                product=product,
                agent=product.supplier,
                action='return',
                quantity_changed=order_item.quantity,
                old_quantity=old_stock,
                new_quantity=product.stock,
                reason=f'Return approved: {return_request.get_return_reason_display()}'
            )
            
            # Mark order item as returned
            order_item.quantity_returned = order_item.quantity
            order_item.return_status = 'completed'
            order_item.save()
            
            # Update return request status
            return_request.status = 'refunded'
            return_request.refunded_at = django.utils.timezone.now()
            return_request.save()
            
            return True
    except Exception as e:
        print(f"Error processing return: {str(e)}")
        return False


def get_agent_dashboard_kpis(agent):
    """
    Calculate real-time KPIs for agent dashboard
    """
    from django.db.models import Sum, Count, Q
    from datetime import datetime, timedelta
    from store.models import SalesTransaction, Order, OrderDelivery, StockAlert
    
    today = django.utils.timezone.now().date()
    this_month = django.utils.timezone.now().date().replace(day=1)
    
    # Orders metrics
    total_orders = Order.objects.filter(items__product__supplier=agent).distinct().count()
    new_orders = OrderDelivery.objects.filter(
        agent=agent,
        delivery_status='not_assigned'
    ).count()
    delivered_orders = OrderDelivery.objects.filter(
        agent=agent,
        delivery_status='delivered'
    ).count()
    
    # Sales metrics
    today_sales = SalesTransaction.objects.filter(
        agent=agent,
        transaction_date__date=today
    ).aggregate(
        revenue=Sum('total_amount'),
        quantity=Sum('quantity')
    )
    
    month_sales = SalesTransaction.objects.filter(
        agent=agent,
        transaction_date__date__gte=this_month
    ).aggregate(
        revenue=Sum('total_amount'),
        quantity=Sum('quantity')
    )
    
    # Stock alerts
    low_stock_count = StockAlert.objects.filter(
        agent=agent,
        is_active=True,
        product__stock__lt=django.db.models.F('threshold_quantity')
    ).count()
    
    # Products
    total_products = agent.products.count()
    out_of_stock = agent.products.filter(stock=0).count()
    
    return {
        'total_orders': total_orders,
        'new_orders': new_orders,
        'delivered_orders': delivered_orders,
        'today_revenue': today_sales.get('revenue') or 0,
        'today_quantity': today_sales.get('quantity') or 0,
        'month_revenue': month_sales.get('revenue') or 0,
        'month_quantity': month_sales.get('quantity') or 0,
        'low_stock_alerts': low_stock_count,
        'total_products': total_products,
        'out_of_stock_count': out_of_stock,
    }