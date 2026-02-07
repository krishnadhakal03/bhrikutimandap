
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
django.setup()

from store.models import HomePage, ContactPage, AuthPage, ProductPageSettings, AgentPageSettings, SiteSettings

def populate():
    print("Populating Dynamic Pages with default content...")

    # 1. Home Page 
    # (Migrate from SiteSettings if present, otherwise default)
    try:
        site_settings = SiteSettings.objects.first()
        trending_title = site_settings.home_trending_title if site_settings else "Trending Product"
        trending_subtitle = site_settings.home_trending_subtitle if site_settings else "Popular Item in the market"
        best_seller_title = site_settings.home_bestseller_title if site_settings else "Best Sellers Shop"
        best_seller_subtitle = site_settings.home_bestseller_subtitle if site_settings else "Amazon global bestselling products"
    except:
        trending_title = "Trending Product"
        trending_subtitle = "Popular Item in the market"
        best_seller_title = "Best Sellers Shop"
        best_seller_subtitle = "Amazon global bestselling products"

    home, _ = HomePage.objects.get_or_create(pk=1)
    home.trending_title = trending_title
    home.trending_subtitle = trending_subtitle
    home.best_seller_title = best_seller_title
    home.best_seller_subtitle = best_seller_subtitle
    home.meta_title = "Bhrikutimandap - Home"
    home.meta_description = "Premium products from local suppliers"
    home.save()
    print("✓ Home Page populated")

    # 2. Contact Page (Default static text from contact.html)
    contact, _ = ContactPage.objects.get_or_create(pk=1)
    contact.contact_title = "Contact Us"
    contact.success_message = "Message sent successfully!"
    contact.meta_title = "Contact Us - Bhrikutimandap"
    contact.save()
    print("✓ Contact Page populated")

    # 3. Auth Page (Default static text from login.html/register.html)
    auth, _ = AuthPage.objects.get_or_create(pk=1)
    auth.login_title = "Log in to enter"
    auth.register_title = "Create an Account"
    auth.login_banner_text = "New to our website?"
    auth.register_banner_text = "Already have an account?"
    auth.meta_title = "Login / Register - Bhrikutimandap"
    auth.save()
    print("✓ Auth Page populated")

    # 4. Product Page Settings
    prod_settings, _ = ProductPageSettings.objects.get_or_create(pk=1)
    prod_settings.add_to_cart_label = "Add to Cart"
    prod_settings.out_of_stock_label = "Out of Stock"
    prod_settings.description_tab_label = "Description"
    prod_settings.reviews_tab_label = "Reviews"
    prod_settings.save()
    print("✓ Product Page Settings populated")

    # 5. Agent Page Settings
    agent_settings, _ = AgentPageSettings.objects.get_or_create(pk=1)
    agent_settings.dashboard_welcome_title = "Agent Dashboard"
    agent_settings.add_product_button_label = "Add New Product"
    agent_settings.products_table_header = "Your Products"
    agent_settings.save()
    print("✓ Agent Page Settings populated")

    print("\nAll dynamic pages seeded successfully!")

if __name__ == "__main__":
    populate()
