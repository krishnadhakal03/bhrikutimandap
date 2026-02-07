from django.test import TestCase, Client
from django.urls import reverse
from store.models import User, Product, Cart, CartItem
from django.core import mail


class RegistrationActivationTest(TestCase):
    def test_registration_and_activation(self):
        c = Client()
        # Use a strong password
        resp = c.post(reverse('store:register'), {
            'username': 'u1', 
            'password': 'StrongPassw0rd!', 
            'email': 'u1@example.com', 
            'role': 'customer'
        })
        # Should redirect to OTP verification page
        self.assertRedirects(resp, reverse('store:verify_otp'))
        
        # OTP email should be in outbox
        self.assertTrue(len(mail.outbox) >= 1)
        body = mail.outbox[0].body
        self.assertIn('Your verification OTP is:', body)

        # Get the OTP from the user object (since we can't easily parse it from email in this test context without regex)
        user = User.objects.get(username='u1')
        otp = user.otp

        # Verify OTP
        # Simulate the session being set (which it is by the register view)
        session = c.session
        session['registration_user_id'] = user.id
        session.save()

        resp = c.post(reverse('store:verify_otp'), {'otp': otp})
        # Should redirect to login or home
        self.assertEqual(resp.status_code, 302)

        # now login (active)
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        
        resp = c.post(reverse('store:login'), {'username':'u1', 'password':'StrongPassw0rd!'})
        self.assertEqual(resp.status_code, 302)


class CartMergeTest(TestCase):
    def setUp(self):
        # Create user with strong password
        self.user = User.objects.create_user(username='buyer', password='StrongPassw0rd!')
        self.prod = Product.objects.create(title='P', price=1.0, stock=10)

    def test_merge_session_cart(self):
        c = Client()
        # add to session cart
        session = c.session
        session['cart'] = {str(self.prod.pk): 2}
        session.save()
        # login view should merge
        resp = c.post(reverse('store:login'), {'username': 'buyer', 'password': 'StrongPassw0rd!'})
        self.assertIn(resp.status_code, (302, 301))
        # ensure cart exists
        cart = Cart.objects.get(user=self.user)
        ci = CartItem.objects.get(cart=cart, product=self.prod)
        self.assertEqual(ci.quantity, 2)
