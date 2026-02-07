import os
import django
from django.core.files import File
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
django.setup()

from store.models import User, AgentProfile, Product, Category, ProductMedia, Order, OrderItem, Address, PaymentMethod

def run():
    print("Generating E2E Data...")
    
    # 1. Create Agent
    agent_username = 'e2e_agent'
    email = 'agent@e2e.com'
    password = 'Password123!'
    
    agent, created = User.objects.get_or_create(username=agent_username, defaults={
        'email': email,
        'role': 'agent',
        'is_active': True,
        'verified': True,
        'approved_by_admin': True
    })
    if created:
        agent.set_password(password)
        agent.save()
        print(f"Created Agent: {agent_username}")
        # Ensure profile
        profile, _ = AgentProfile.objects.get_or_create(user=agent, defaults={
            'company_name': 'E2E Tech Suppliers',
            'phone': '9800000000',
            'approval_status': 'approved',
            'is_verified': True
        })
    else:
        print(f"Agent {agent_username} already exists.")

    # 2. Create Category
    category, _ = Category.objects.get_or_create(name='E2E Electronics', slug='e2e-electronics')
    
    # 3. Create Product with Multiple Images
    product_title = 'E2E Multi-Image Product'
    
    # Check if images exist in static
    static_img_dir = os.path.join(settings.BASE_DIR, 'static', 'img')
    img1_path = os.path.join(static_img_dir, 'r1.jpg')
    img2_path = os.path.join(static_img_dir, 'r2.jpg')
    
    if not os.path.exists(img1_path):
        print(f"Warning: {img1_path} not found. Skipping image upload.")
        return

    from django.core.files.images import ImageFile
    
    product, created = Product.objects.get_or_create(title=product_title, defaults={
        'category': category,
        'price': 1500.00,
        'stock': 50,
        'description': 'This product was created by the E2E generation script. It should have multiple images.',
        'supplier': agent
    })
    
    if created:
        # Add main image
        with open(img1_path, 'rb') as f:
            product.image.save('e2e_main.jpg', File(f), save=True)
        print(f"Created Product: {product_title}")
        
        # Add additional media
        if os.path.exists(img2_path):
            with open(img2_path, 'rb') as f:
                ProductMedia.objects.create(product=product, file=File(f, name='e2e_extra.jpg'), media_type='image')
            print("Added additional image.")
    else:
        print(f"Product {product_title} already exists.")

    # 4. Create Customer
    cust_username = 'e2e_customer'
    customer, created = User.objects.get_or_create(username=cust_username, defaults={
        'email': 'customer@e2e.com',
        'role': 'customer',
        'is_active': True
    })
    if created:
        customer.set_password(password)
        customer.save()
        print(f"Created Customer: {cust_username}")
    
    # 5. Create Address
    address, _ = Address.objects.get_or_create(user=customer, label='Home', defaults={
        'recipient_name': 'E2E Tester',
        'city': 'Kathmandu',
        'phone': '9800000000'
    })

    print("Data Generation Complete.")

if __name__ == '__main__':
    run()
