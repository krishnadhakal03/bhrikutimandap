from django.core.management.base import BaseCommand
from django.template.loader import get_template
from django.template import Template, Context

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Load agent/dashboard.html template
        try:
            template = get_template('agent/dashboard.html')
            self.stdout.write("Loaded agent/dashboard.html successfully")
            
            # Try to render it with a fake context
            from django.contrib.auth.models import AnonymousUser
            from django.test.client import RequestFactory
            
            factory = RequestFactory()
            request = factory.get('/agent/dashboard/')
            from store.models import User
            request.user = User.objects.get(username='agent1')
            
            context = {
                'request': request,
                'total_revenue': 1000,
                'total_sales': 50,
                'total_orders': 5,
                'total_products': 2,
                'low_stock_count': 0,
                'top_products': [],
                'recent_sales': [],
                'days_back': 30,
                'product_count': 2,
                'agent_profile': None,
                'user': request.user,
            }
            
            html = template.render(context, request)
            
            # Check for agent portal header
            if 'Agent Portal' in html and 'agent-header' in html:
                self.stdout.write(self.style.SUCCESS("SUCCESS: Agent portal header found"))
            else:
                self.stdout.write(self.style.ERROR("FAIL: Agent portal header NOT found"))
            
            # Check for customer header
            if 'header_area' in html:
                self.stdout.write(self.style.ERROR("FAIL: Customer header_area class found (should not be there)"))
            else:
                self.stdout.write(self.style.SUCCESS("SUCCESS: Customer header_area class not found"))
                
            # Look for key strings
            if 'Bhrikutimandap - Agent Portal' in html:
                self.stdout.write("  - Found: 'Bhrikutimandap - Agent Portal'")
            else:
                self.stdout.write("  - NOT found: 'Bhrikutimandap - Agent Portal'")
                
            if 'agent-sidebar' in html:
                self.stdout.write("  - Found: 'agent-sidebar'")
            else:
                self.stdout.write("  - NOT found: 'agent-sidebar'")
                
            # Save output for inspection
            with open('debug_template_render.html', 'w', encoding='utf-8') as f:
                f.write(html)
            self.stdout.write("\nFull HTML saved to debug_template_render.html")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
            import traceback
            traceback.print_exc()
