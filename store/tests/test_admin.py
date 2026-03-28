from django.test import TestCase, Client
from django.urls import reverse
from store.models import User, Product, AgentProfile, HomePage, SiteSettings

class AdminModuleTest(TestCase):
    def setUp(self):
        self.client = Client()
        SiteSettings.get_instance()
        # Create superuser
        self.admin_user = User.objects.create_superuser(username='admin', password='password', email='admin@test.com')
        self.client.force_login(self.admin_user)
        
        # Create an agent for approval test
        self.agent = User.objects.create_user(username='pending_agent', password='password', role='agent')
        # Profile should be auto-created by signal now
        
    def test_agent_approval_via_admin(self):
        # Ensure agent exists and is not verified
        self.assertFalse(self.agent.verified)
        
        url = reverse('admin:store_user_changelist')
        # Django admin actions require post=yes for some actions, or just the action name
        data = {
            'action': 'approve_users',
            '_selected_action': [str(self.agent.id)],
            'apply': 'Go' # Some versions use this
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        
        self.agent.refresh_from_db()
        self.assertTrue(self.agent.verified)
        self.assertTrue(self.agent.approved_by_admin)

    def test_product_actions_stock(self):
        product = Product.objects.create(title='Bug Product', price=10.0, stock=0)
        url = reverse('admin:store_product_changelist')
        data = {
            'action': 'mark_in_stock',
            '_selected_action': [str(product.id)],
            'apply': 'Go'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
            
        product.refresh_from_db()
        self.assertEqual(product.stock, 10)

    def test_homepage_crud(self):
        # Ensure it exists with PK=1
        HomePage.load()
        url = reverse('admin:store_homepage_change', args=[1])
        data = {
            'meta_title': 'New Title',
            'meta_description': 'New Desc',
            'meta_keywords': 'K1, K2',
            'trending_title': 'Trending Now',
            'trending_subtitle': 'Sub',
            'best_seller_title': 'Best Cells',
            'best_seller_subtitle': 'Sub2',
            'featured_title': 'Featured Picks',
            'featured_subtitle': 'Handpicked highlights from verified sellers.',
            '_save': 'Save'
        }
        response = self.client.post(url, data)
        if response.status_code != 302:
             # If it failed, print errors for debugging
             if 'adminform' in response.context:
                 print(f"Form Errors: {response.context['adminform'].form.errors}")
        
        self.assertEqual(response.status_code, 302)
        
        hp = HomePage.load()
        self.assertEqual(hp.meta_title, 'New Title')
