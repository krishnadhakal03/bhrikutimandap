from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Seed the database with sample agents (suppliers), customers, products, and site settings'

    def handle(self, *args, **options):
        from store.models import Product, User, SiteSettings, CustomerProfile
        
        # Create or update SiteSettings
        settings = SiteSettings.get_instance()
        if not hasattr(settings, 'id') or settings.id is None:
            settings.save()
        self.stdout.write('SiteSettings configured')

        # Create test admin user
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(username='admin', email='admin@bhrikutimandap.com', password='admin123', role='admin')
            admin_user.approved_by_admin = True
            admin_user.verified = True
            admin_user.save()
            self.stdout.write('Created admin user: admin / admin123')

        # Create sample agents (suppliers)
        agents = [
            {
                'username': 'agent1',
                'email': 'agent1@bhrikutimandap.com',
                'first_name': 'Ramesh',
                'last_name': 'Organics',
                'company': 'Ramesh Organic Farm',
                'phone': '+91 9876543210',
                'city': 'Delhi',
                'country': 'India',
            },
            {
                'username': 'agent2',
                'email': 'agent2@bhrikutimandap.com',
                'first_name': 'Priya',
                'last_name': 'Crafts',
                'company': 'Priya Handicrafts',
                'phone': '+91 9123456789',
                'city': 'Bangalore',
                'country': 'India',
            },
            {
                'username': 'agent3',
                'email': 'agent3@bhrikutimandap.com',
                'first_name': 'Arjun',
                'last_name': 'Dairy',
                'company': 'Arjun Family Dairy',
                'phone': '+91 8765432109',
                'city': 'Mumbai',
                'country': 'India',
            },
        ]

        for agent_data in agents:
            username = agent_data['username']
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(password='agent123', role='agent', is_active=True, **agent_data)
                user.approved_by_admin = True
                user.verified = True
                user.save()
                self.stdout.write(f'Created agent: {username} / agent123')
            else:
                user = User.objects.get(username=username)
                self.stdout.write(f'Agent {username} already exists')

        # Create test customer users
        customers = [
            {
                'username': 'customer1',
                'email': 'customer1@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone': '+1 9876543210',
                'city': 'New York',
                'country': 'USA',
            },
            {
                'username': 'customer2',
                'email': 'customer2@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'phone': '+1 9123456789',
                'city': 'Los Angeles',
                'country': 'USA',
            },
        ]

        for cust_data in customers:
            username = cust_data['username']
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(password='customer123', role='customer', is_active=True, **cust_data)
                CustomerProfile.objects.get_or_create(user=user)
                self.stdout.write(f'Created customer: {username} / customer123')
            else:
                user = User.objects.get(username=username)
                CustomerProfile.objects.get_or_create(user=user)

        # Create sample products from agents
        if Product.objects.exists():
            self.stdout.write('Products already exist; skipping product creation')
            return

        products_by_agent = {
            'agent1': [
                {
                    'title': 'Organic Tomatoes',
                    'description': 'Fresh, pesticide-free tomatoes from our farm',
                    'price': 50.00,
                    'stock': 100,
                    'delivery_rules': 'Free delivery within 10km; Ships next day',
                    'payment_methods': 'Cash on Delivery, UPI, Bank Transfer',
                    'expiration_date': timezone.now() + timedelta(days=7),
                },
                {
                    'title': 'Organic Carrots',
                    'description': 'Crunchy, orange carrots without chemicals',
                    'price': 40.00,
                    'stock': 150,
                    'delivery_rules': 'Free delivery within 10km',
                    'payment_methods': 'COD, UPI',
                    'expiration_date': timezone.now() + timedelta(days=14),
                },
            ],
            'agent2': [
                {
                    'title': 'Handmade Ceramic Bowl',
                    'description': 'Beautiful ceramic bowl, handcrafted',
                    'price': 300.00,
                    'stock': 25,
                    'delivery_rules': 'Ships within 5 business days',
                    'payment_methods': 'Card, UPI, Bank Transfer',
                },
                {
                    'title': 'Wooden Serving Tray',
                    'description': 'Elegant wooden tray for serving',
                    'price': 250.00,
                    'stock': 15,
                    'delivery_rules': 'Ships within 3 days',
                    'payment_methods': 'Card, UPI, COD',
                },
            ],
            'agent3': [
                {
                    'title': 'Fresh Paneer',
                    'description': 'Fresh cow milk paneer, prepared daily',
                    'price': 200.00,
                    'stock': 50,
                    'delivery_rules': 'Free delivery within 5km; Hot delivery in insulated box',
                    'payment_methods': 'COD, UPI',
                    'expiration_date': timezone.now() + timedelta(days=3),
                },
                {
                    'title': 'Homemade Ghee',
                    'description': 'Pure ghee from grass-fed cows',
                    'price': 350.00,
                    'stock': 30,
                    'delivery_rules': 'Insulated packaging; Free delivery >500 order',
                    'payment_methods': 'COD, Card, UPI',
                },
            ],
        }

        try:
            from PIL import Image, ImageDraw, ImageFont
            import io
            has_pillow = True
        except Exception:
            has_pillow = False
            self.stdout.write('Pillow not installed; creating products without images')

        for agent_username, products_list in products_by_agent.items():
            agent = User.objects.get(username=agent_username)
            for idx, prod_data in enumerate(products_list, start=1):
                prod = Product.objects.create(supplier=agent, **prod_data)
                
                if has_pillow:
                    # Generate a placeholder image
                    img = Image.new('RGB', (400, 300), color=(100, 150, 200))
                    d = ImageDraw.Draw(img)
                    text = prod_data['title'][:20]
                    try:
                        font = ImageFont.load_default()
                        d.text((20, 20), text, fill=(255, 255, 255), font=font)
                    except Exception:
                        d.text((20, 20), text, fill=(255, 255, 255))
                    buf = io.BytesIO()
                    img.save(buf, format='PNG')
                    buf.seek(0)
                    prod.image.save(f'{agent_username}_product_{idx}.png', buf)
                    prod.save()
                
                self.stdout.write(f'Created product: {prod.title} by {agent_username}')

        self.stdout.write(self.style.SUCCESS('Database seeded successfully'))
        self.stdout.write('Test credentials:')
        self.stdout.write('  Admin: admin / admin123')
        self.stdout.write('  Agent: agent1 / agent123 (or agent2, agent3)')
        self.stdout.write('  Customer: customer1 / customer123 (or customer2)')
