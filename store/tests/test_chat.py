from django.test import Client, TestCase
from django.urls import reverse

from store.models import Category, Product, SellerConversation, SellerMessage, User


class ChatEndpointsTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.customer = User.objects.create_user(
            username='chat_customer',
            email='chat_customer@example.com',
            password='StrongPassw0rd!',
            role='customer',
        )
        self.other_customer = User.objects.create_user(
            username='chat_other_customer',
            email='chat_other_customer@example.com',
            password='StrongPassw0rd!',
            role='customer',
        )
        self.agent = User.objects.create_user(
            username='chat_agent',
            email='chat_agent@example.com',
            password='StrongPassw0rd!',
            role='agent',
        )

        self.category = Category.objects.create(name='General', slug='general')
        self.product = Product.objects.create(
            category=self.category,
            supplier=self.agent,
            title='Chat Product',
            description='Product used for chat tests.',
            price='120.00',
            stock=10,
        )

        self.conversation = SellerConversation.objects.create(
            customer=self.customer,
            seller=self.agent,
            product=self.product,
        )

        SellerMessage.objects.create(
            conversation=self.conversation,
            sender=self.agent,
            body='Hello customer',
            is_read=False,
        )

    def test_chat_unread_counts_for_customer(self):
        self.client.login(username='chat_customer', password='StrongPassw0rd!')

        response = self.client.get(reverse('store:chat_unread_counts_api'))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['customer_unread'], 1)
        self.assertEqual(data['agent_unread'], 0)
        self.assertEqual(data['total_unread'], 1)

    def test_chat_unread_counts_for_agent(self):
        self.client.login(username='chat_agent', password='StrongPassw0rd!')

        response = self.client.get(reverse('store:chat_unread_counts_api'))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['customer_unread'], 0)
        self.assertEqual(data['agent_unread'], 1)
        self.assertEqual(data['total_unread'], 1)

    def test_customer_messages_requires_login(self):
        response = self.client.get(reverse('store:customer_messages'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('store:login'), response.url)

    def test_customer_messages_marks_incoming_as_read(self):
        self.client.login(username='chat_customer', password='StrongPassw0rd!')

        response = self.client.get(reverse('store:customer_messages_detail', args=[self.conversation.id]))
        self.assertEqual(response.status_code, 200)

        unread_exists = SellerMessage.objects.filter(
            conversation=self.conversation,
            sender=self.agent,
            is_read=False,
        ).exists()
        self.assertFalse(unread_exists)

    def test_customer_cannot_open_other_customers_conversation(self):
        other_conv = SellerConversation.objects.create(
            customer=self.other_customer,
            seller=self.agent,
            product=self.product,
        )
        self.client.login(username='chat_customer', password='StrongPassw0rd!')

        response = self.client.get(reverse('store:customer_messages_detail', args=[other_conv.id]))
        self.assertEqual(response.status_code, 404)
