from django.test import TestCase, Client
from django.urls import reverse
from store.models import User, SiteSettings, AuthPage
from django.core import mail
from datetime import timedelta
from django.utils import timezone

class AuthTest(TestCase):
    def setUp(self):
        self.client = Client()
        SiteSettings.get_instance()
        AuthPage.load()
        
    def test_customer_registration_flow(self):
        # 1. Register
        url = reverse('store:register')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'StrongPassword123!',
            'role': 'customer'
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('store:verify_otp'))
        
        # 2. Check User Created (Inactive)
        user = User.objects.get(username='newuser')
        self.assertFalse(user.is_active)
        self.assertTrue(user.otp)
        
        # 3. Check OTP Email matched
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(user.otp, mail.outbox[0].body)
        
        # 4. Verify OTP
        otp_url = reverse('store:verify_otp')
        # Session must have user_id
        session = self.client.session
        session['registration_user_id'] = user.id
        session.save()
        
        response = self.client.post(otp_url, {'otp': user.otp})
        
        # 5. Should redirect to Login (or Product List if auto-login, depending on view logic)
        # Checking view logic: verify_otp redirects to 'store:login' usually
        self.assertRedirects(response, reverse('store:login'))
        
        # 6. Check User Active
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        
    def test_login_flow(self):
        # Create active user
        user = User.objects.create_user(username='loginuser', email='l@e.com', password='pass', role='customer')
        
        url = reverse('store:login')
        response = self.client.post(url, {'username': 'loginuser', 'password': 'pass'})
        
        # Should redirect to product_list for customer
        self.assertRedirects(response, reverse('store:product_list'))
        
        # Check session
        self.assertTrue('_auth_user_id' in self.client.session)
