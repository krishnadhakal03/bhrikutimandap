#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
django.setup()

from store.admin import BlogAdmin

print("\n=== Testing BlogAdmin.form ===")
try:
    from django.contrib.admin.sites import AdminSite
    from store.models import Blog
    admin_site = AdminSite()
    blog_admin = BlogAdmin(Blog, admin_site)
    print(f'✓ BlogAdmin instantiated')
    print(f'BlogAdmin.form: {blog_admin.form}')
    
    # Try instantiating the form
    form = blog_admin.form()
    print('✓ BlogForm instantiated successfully')
    print(f'Content field widget: {form.fields["content"].widget}')
    print(f'Widget class: {type(form.fields["content"].widget).__name__}')
    
    # Try rendering the widget
    rendered = str(form['content'])
    print(f'✓ Content field renders: {len(rendered)} chars')
    if 'ckeditor' in rendered.lower():
        print('✓ CKEditor found in rendered output')
except Exception as e:
    print(f'✗ Error: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
