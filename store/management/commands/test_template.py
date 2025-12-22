from django.core.management.base import BaseCommand
from django.test import Client
from store.models import User
import codecs

class Command(BaseCommand):
    help = 'Test template rendering for agent dashboard'

    def handle(self, *args, **options):
        # Get agent user
        agent = User.objects.filter(username='agent1').first()
        if not agent:
            self.stdout.write(self.style.ERROR("Agent not found!"))
            return

        self.stdout.write(f"Testing agent dashboard rendering for: {agent.username}")
        self.stdout.write(f"Agent role: {agent.role}")
        self.stdout.write(f"Agent is active: {agent.is_active}")

        # Create client and login
        client = Client()
        login_success = client.login(username='agent1', password='agent123')
        self.stdout.write(f"\nLogin success: {login_success}")

        # Get dashboard
        try:
            response = client.get('/agent/dashboard/', follow=True)
            self.stdout.write(f"Dashboard URL: /agent/dashboard/")
            self.stdout.write(f"Response status: {response.status_code}")
            self.stdout.write(f"Response URL: {response.request.get('PATH_INFO', 'N/A')}")
            
            # Check if there are any exceptions
            if hasattr(response, 'exc_info') and response.exc_info:
                import traceback
                self.stdout.write(self.style.ERROR("Exception occurred:"))
                self.stdout.write(''.join(traceback.format_exception(*response.exc_info)))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error getting dashboard: {e}"))
            import traceback
            traceback.print_exc()
            return

        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Save full response for inspection
            with open('debug_response.html', 'w', encoding='utf-8') as f:
                f.write(content)
            self.stdout.write("Full response saved to debug_response.html")
            
            # Find the <body> tag to see what's rendered
            body_start = content.find('<body')
            if body_start != -1:
                body_content = content[body_start:body_start+2000]
                self.stdout.write(f"\n=== BODY CONTENT (first 2000 chars) ===")
                self.stdout.write(body_content)
                self.stdout.write("======================================\n")
            
            # Search for key markers
            self.stdout.write("\n=== KEY CONTENT CHECKS ===")
            
            agent_portal_count = content.count('Agent Portal')
            self.stdout.write(f"Occurrences of 'Agent Portal': {agent_portal_count}")
            
            agent_header_count = content.count('agent-header')
            self.stdout.write(f"Occurrences of 'agent-header': {agent_header_count}")
            
            agent_sidebar_count = content.count('agent-sidebar')
            self.stdout.write(f"Occurrences of 'agent-sidebar': {agent_sidebar_count}")
            
            customer_menu_count = content.count('Home | Shop | Contact')
            self.stdout.write(f"Occurrences of 'Home | Shop | Contact': {customer_menu_count}")
            
            # Find position of agent portal header if it exists
            if 'Agent Portal' in content:
                pos = content.find('Agent Portal')
                self.stdout.write(f"\n'Agent Portal' found at position {pos}")
                self.stdout.write(f"Context: ...{content[max(0, pos-100):pos+200]}...")
            else:
                self.stdout.write("\n'Agent Portal' NOT found in entire response")
            
            # Check for agent-header class in style
            if '.agent-header' in content:
                self.stdout.write("✅ .agent-header CSS found")
            else:
                self.stdout.write("❌ .agent-header CSS NOT found")
            
            self.stdout.write("===========================\n")
            
            # Check for agent portal header
            if 'Agent Portal' in content and 'Bhrikutimandap - Agent Portal' in content:
                self.stdout.write(self.style.SUCCESS("✅ GOOD: Agent portal header found in HTML"))
            else:
                self.stdout.write(self.style.ERROR("❌ BAD: Agent portal header NOT found in HTML"))
            
            # Check for customer header
            if 'Home | Shop | Contact' in content or ('<li class="nav-item"><a class="nav-link" href' in content and 'Home' in content):
                self.stdout.write(self.style.ERROR("❌ BAD: Customer header found in HTML (should not be there)"))
            else:
                self.stdout.write(self.style.SUCCESS("✅ GOOD: Customer header NOT in HTML"))
            
            # Check for sidebar
            if 'agent-sidebar' in content or 'Dashboard' in content and 'Products' in content and 'Stock' in content:
                self.stdout.write(self.style.SUCCESS("✅ GOOD: Agent sidebar indicators found"))
            else:
                self.stdout.write(self.style.ERROR("❌ BAD: Agent sidebar NOT found"))
            
            # Check for specific agent menu items
            menu_items = ['Dashboard', 'Products', 'Stock', 'Sales', 'Reports', 'Orders']
            for item in menu_items:
                if item in content:
                    self.stdout.write(f"  ✅ Menu item '{item}' found")
                else:
                    self.stdout.write(f"  ❌ Menu item '{item}' NOT found")

        else:
            self.stdout.write(f"Error: Got status {response.status_code}")
