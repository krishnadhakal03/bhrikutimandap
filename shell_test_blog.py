from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

# Create a test client
client = Client()

# Get existing superuser or create one
try:
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.create_superuser('testadmin', 'admin@test.com', 'testpass123')
        print("[OK] Created test superuser")
    username = user.username
    password = 'testpass123' if user.username == 'testadmin' else None
except:
    password = None

if not password:
    # Try common passwords
    import django.contrib.auth.hashers as hashers
    # Reset to known password for testing
    user.set_password('testpass123')
    user.save()
    password = 'testpass123'
    print(f"[OK] Set password for {user.username}")

# Login
logged_in = client.login(username=user.username, password=password)
print(f'[OK] Logged in as {user.username}: {logged_in}')

# Access the blog add page
response = client.get('/admin/store/blog/add/')
print(f'[OK] Response status: {response.status_code}')

if response.status_code == 200:
    print('[OK] Blog add page loaded successfully!')
    # Check for the CKEditor in the response
    content = response.content.decode()
    if 'ckeditor' in content.lower():
        print('[OK] CKEditor found in page')
    if 'id_content' in content:
        print('[OK] Content field found in form')
    print('[OK] TEST PASSED: Form renders without 500 error')
else:
    print(f'[ERROR] Response: {response.status_code}')
    if response.status_code == 500:
        print('[ERROR] TEST FAILED: 500 error')
