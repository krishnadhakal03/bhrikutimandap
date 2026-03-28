from django.test import TestCase, Client
from django.urls import reverse
from store.models import User, AgentProfile, Product, Category, SiteSettings, AgentPageSettings

class AgentJourneyTest(TestCase):
    def setUp(self):
        self.client = Client()
        SiteSettings.get_instance()
        AgentPageSettings.load()
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        
    def test_agent_registration(self):
        url = reverse('store:register')
        data = {
            'username': 'agent007',
            'email': 'agent@test.com',
            'password': 'Password@123',
            'role': 'agent',
            'company': 'Bond Industries',
            'phone': '9800000000',
            # Add any other required fields here if needed
        }
        response = self.client.post(url, data)
        
        # Should redirect to OTP verification
        self.assertRedirects(response, reverse('store:verify_otp'))
        
        # Check User
        user = User.objects.get(username='agent007')
        self.assertEqual(user.role, 'agent')
        self.assertFalse(user.is_active)
        
        # Check Profile
        profile = AgentProfile.objects.get(user=user)
        self.assertEqual(profile.company_name, 'Bond Industries')
        # Assuming default is pending
        self.assertEqual(profile.approval_status, 'pending')

    def test_agent_dashboard_access(self):
        # Create active verified agent
        user = User.objects.create_user(username='activeagent', password='password', role='agent')
        # Signal should create profile, but let's ensure it's approved
        profile = AgentProfile.objects.get(user=user)
        profile.approval_status = 'approved'
        profile.is_verified = True
        profile.save()
        
        self.client.force_login(user)
        
        url = reverse('agent:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_product_creation(self):
        # Create active approved agent
        user = User.objects.create_user(username='supplier', password='password', role='agent')
        profile = AgentProfile.objects.get(user=user)
        profile.approval_status = 'approved'
        profile.save()
        
        self.client.force_login(user)
        
        from django.core.files.uploadedfile import SimpleUploadedFile
        # Minimal 1x1 GIF
        valid_gif = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        
        # Additional media
        image = SimpleUploadedFile(name='test_image.gif', content=valid_gif, content_type='image/gif')
        image2 = SimpleUploadedFile(name='test_image2.gif', content=valid_gif, content_type='image/gif')
        image3 = SimpleUploadedFile(name='test_image3.gif', content=valid_gif, content_type='image/gif')
        
        url = reverse('agent:product_create')
        data = {
            'title': 'New Gadget',
            'category': self.category.id,
            'price': 5000,
            'stock': 100,
            'description': 'Best gadget',
            'image': image,
            'additional_media': [image2, image3]  # List for getlist
        }
        response = self.client.post(url, data, follow=True)
        
        if response.context and 'form' in response.context:
            if response.context['form'].errors:
                 print(f"Form Errors: {response.context['form'].errors}")

        # Check if product exists first
        self.assertTrue(Product.objects.filter(title='New Gadget').exists())
        product = Product.objects.get(title='New Gadget')
        self.assertEqual(product.supplier, user)
        
        # Check additional media
        from store.models import ProductMedia
        self.assertEqual(ProductMedia.objects.filter(product=product).count(), 2)
        
    def test_customer_access_denied(self):
        # Customer tries to access dashboard
        customer = User.objects.create_user(username='cust', password='pwm', role='customer')
        self.client.force_login(customer)
        
        url = reverse('agent:dashboard')
        response = self.client.get(url)
        
        # Expect redirect to home or login or 403
        # Depending on @user_passes_test logic. Usually redirects to login if failed.
        self.assertNotEqual(response.status_code, 200)
