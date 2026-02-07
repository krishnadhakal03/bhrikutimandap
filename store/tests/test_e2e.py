from django.test import TestCase, Client
from django.urls import reverse
from store.models import User, Product, Category, Cart, Order, Address, PaymentMethod, SiteSettings

class EndToEndTest(TestCase):
    def setUp(self):
        self.client = Client()
        SiteSettings.get_instance()
        self.cat = Category.objects.create(name='Electronics', slug='electronics')
        self.agent = User.objects.create_user(username='agent', password='password', role='agent')
        self.product = Product.objects.create(
            title='Smartphone', 
            price=20000.0, 
            stock=10, 
            category=self.cat, 
            supplier=self.agent
        )
        self.user = User.objects.create_user(username='customer', password='password', role='customer')
        self.user.is_active = True
        self.user.save()
        
    def test_complete_customer_journey(self):
        # 1. Login
        self.client.post(reverse('store:login'), {'username': 'customer', 'password': 'password'})
        
        # 2. Search/Browse
        response = self.client.get(reverse('store:product_list'), {'q': 'Smartphone'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Smartphone')
        
        # 3. Add to Cart
        self.client.post(reverse('store:api_cart_add'), {'product_id': self.product.id, 'qty': 1}, content_type='application/json')
        
        # 4. Checkout
        addr = Address.objects.create(user=self.user, city='Pokhara', state='Gandaki')
        pm = PaymentMethod.objects.create(user=self.user, payment_type='COD')
        
        response = self.client.post(reverse('store:checkout'), {
            'delivery_address': addr.id,
            'payment_method': pm.id
        })
        self.assertEqual(response.status_code, 302) # Redirect to order detail
        
        # 5. Verify Order Creation
        self.assertTrue(Order.objects.filter(user=self.user).exists())
        order = Order.objects.get(user=self.user)
        self.assertEqual(order.total(), 20000.0)
        
        # 6. Verify Stock
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 9)
