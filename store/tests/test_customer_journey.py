from django.test import TestCase, Client
from django.urls import reverse
from store.models import User, Product, Cart, CartItem, Address, PaymentMethod, SiteSettings, ProductPageSettings

class CustomerJourneyTest(TestCase):
    def setUp(self):
        self.client = Client()
        SiteSettings.get_instance()
        ProductPageSettings.load()
        # Create user
        self.user = User.objects.create_user(username='shopper', password='password', role='customer')
        self.user.is_active = True
        self.user.save()
        
        # Create product
        self.product = Product.objects.create(title='Test Product', price=100.0, stock=50)
        
    def test_product_browsing(self):
        url = reverse('store:product_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')
        
    def test_add_to_cart_anonymous(self):
        url = reverse('store:api_cart_add')
        # API requires POST JSON
        data = {'product_id': self.product.id, 'qty': 2}
        response = self.client.post(url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['ok'], True)
        
        # Verify session
        session = self.client.session
        self.assertEqual(session['cart'][str(self.product.id)], 2)
        
    def test_add_to_cart_authenticated(self):
        self.client.force_login(self.user)
        url = reverse('store:api_cart_add')
        data = {'product_id': self.product.id, 'qty': 3}
        response = self.client.post(url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # Verify DB
        cart = Cart.objects.get(user=self.user)
        item = CartItem.objects.get(cart=cart, product=self.product)
        self.assertEqual(item.quantity, 3)
        
    def test_full_customer_journey(self):
        # 1. Login
        self.client.force_login(self.user)
        
        # 2. Search Product
        url = reverse('store:product_list')
        response = self.client.get(url, {'search': 'Test Product'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')
        
        # 3. Add to Cart (using API)
        url = reverse('store:api_cart_add')
        data = {'product_id': self.product.id, 'qty': 1}
        response = self.client.post(url, data, content_type='application/json')
        self.assertTrue(response.json()['ok'])
        
        # 4. Update Cart (Increment)
        url = reverse('store:api_cart_update')
        data = {'product_id': self.product.id, 'qty': 2}
        response = self.client.post(url, data, content_type='application/json')
        self.assertTrue(response.json()['ok'])
        
        # Verify Cart State
        cart = Cart.objects.get(user=self.user)
        item = CartItem.objects.get(cart=cart, product=self.product)
        self.assertEqual(item.quantity, 2)
        
        # 5. Remove Item (Verify it works)
        url = reverse('store:api_cart_remove')
        data = {'product_id': self.product.id}
        response = self.client.post(url, data, content_type='application/json')
        self.assertTrue(response.json()['ok'])
        self.assertFalse(CartItem.objects.filter(cart=cart, product=self.product).exists())
        
        # 6. Add Back for Checkout
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)
        
        # 7. Checkout with COD
        # Create Address first
        address = Address.objects.create(user=self.user, city='Pokhara', state='Gandaki', label='Home')
        
        url = reverse('store:checkout')
        data = {
            'delivery_address': address.id,
            'payment_method': 'cod'  # Using new COD option
        }
        response = self.client.post(url, data)
        
        # Expect redirect to order detail
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/order/'))
        
        # Verify Order
        from store.models import Order
        order = Order.objects.filter(user=self.user).latest('created_at')
        self.assertEqual(order.delivery_address, address)
        # Payment method should be COD (we created it properly)
        self.assertEqual(order.payment_method.payment_type, 'cod')
        
        # Check stock reduced
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 49)
