from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Product, Cart, CartItem
from django.core import mail


class RegistrationActivationTest(TestCase):
    def test_registration_and_activation(self):
        c = Client()
        resp = c.post(reverse('store:register'), {'username': 'u1', 'password': 'StrongPassw0rd!', 'email': 'u1@example.com', 'role':'customer'})
        self.assertEqual(resp.status_code, 302)
        # Activation email should be in console (outbox in tests)
        self.assertTrue(len(mail.outbox) >= 1)
        # extract activation link
        body = mail.outbox[0].body
        import re
        m = re.search(r'http://[^\s]+', body)
        self.assertIsNotNone(m)
        link = m.group(0)
        # follow activation link
        resp = c.get(link)
        self.assertEqual(resp.status_code, 302)
        # now login should work
        resp = c.post(reverse('store:login'), {'username':'u1','password':'StrongPassw0rd!'})
        self.assertEqual(resp.status_code, 302)


class CartMergeTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='buyer', password='pass')
        self.prod = Product.objects.create(title='P', price=1.0, stock=10)

    def test_merge_session_cart(self):
        c = Client()
        # add to session cart
        session = c.session
        session['cart'] = {str(self.prod.pk): 2}
        session.save()
        # login view should merge
        resp = c.post(reverse('store:login'), {'username': 'buyer', 'password': 'pass'})
        self.assertIn(resp.status_code, (302, 301))
        # ensure cart exists
        cart = Cart.objects.get(user=self.user)
        ci = CartItem.objects.get(cart=cart, product=self.prod)
        self.assertEqual(ci.quantity, 2)
