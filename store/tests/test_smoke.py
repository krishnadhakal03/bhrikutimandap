from django.test import TestCase, Client
from django.urls import reverse
from store.models import SiteSettings, HomePage, ContactPage, AuthPage, ProductPageSettings, AgentPageSettings

class SmokeTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Seed singleton models to avoid 500s if views expect them
        SiteSettings.get_instance()
        HomePage.load()
        ContactPage.load()
        AuthPage.load()
        ProductPageSettings.load()
        AgentPageSettings.load()

    def test_home_page_status(self):
        url = reverse('store:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_contact_page_status(self):
        url = reverse('store:contact')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_login_page_status(self):
        url = reverse('store:login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_register_page_status(self):
        url = reverse('store:register')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_admin_login_page(self):
        # Admin URL is usually /admin/login/
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, 200)
