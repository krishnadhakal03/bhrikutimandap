# 🛍️ Bhrikutimandap - E-Commerce Platform

A comprehensive, role-based e-commerce platform built with Django, featuring customer portal, agent/supplier dashboard, and advanced delivery management system.

## 🌟 Key Features

### Customer Features
- 👤 **User Management**: Registration, profile management, address book, payment methods
- 🛍️ **Product Browsing**: Advanced search, filtering by price and supplier, product details
- 🛒 **Shopping Cart**: Add/remove items, quantity management, persistent cart
- 💳 **Checkout**: Multi-step checkout with address and payment selection
- 📦 **Order Management**: Order history, order tracking, delivery status updates
- ❤️ **Wishlist**: Save favorite products for later
- 📝 **Returns**: Request product returns with reason and tracking

### Agent/Supplier Features
- 📊 **Dashboard**: Real-time metrics, revenue tracking, sales graphs
- 📦 **Product Management**: Add, edit, delete products with inventory
- 📈 **Stock Management**: Inventory adjustment, low stock alerts, stock alerts
- 💰 **Sales Tracking**: Sales history, revenue reports, analytics
- 📋 **Order Management**: Incoming orders, order processing, order tracking
- 🚚 **Delivery Management**: 
  - Delivery partner management with contact info
  - Vehicle management (bikes, autos, cars, trucks, vans)
  - Assign specific vehicles to orders
  - Real-time delivery tracking with status updates
  - Delivery timeline visualization
- 📊 **Reports & Analytics**: Revenue charts, sales summaries, market insights
- 🔄 **Return Management**: Handle customer return requests

### Admin Features
- 🎛️ **Admin Panel**: Full Django admin with custom styling
- 👥 **User Management**: Customer and agent accounts
- 📦 **Product Catalog**: Global product management
- 📋 **Order Management**: All orders across all agents
- 🚚 **Delivery System**: Manage delivery partners and vehicles
- 📊 **Analytics**: Platform-wide statistics and reporting

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Django 5.2.5
- SQLite (included)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/krishnadhakal03/bhrikutimandap.git
cd bhrikutimandap
```

2. **Create and activate virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Create superuser (admin)**
```bash
python manage.py createsuperuser
```

6. **Load sample data (optional)**
```bash
python manage.py seed
```

7. **Start development server**
```bash
python manage.py runserver 8000
```

8. **Access the platform**
- Customer Portal: http://localhost:8000/
- Admin Panel: http://localhost:8000/admin/
- Agent Dashboard: http://localhost:8000/agent/dashboard/

---

## 🚀 Deployment

### Deploy to Hostinger

Ready to deploy your application to production? We've got you covered with comprehensive deployment documentation:

- **[QUICK_DEPLOYMENT.md](QUICK_DEPLOYMENT.md)** ⚡ **START HERE**
  - 30-minute quick start guide
  - Essential steps only
  - Perfect for getting started fast

- **[DEPLOYMENT.md](DEPLOYMENT.md)** 📖 Complete Guide
  - Detailed step-by-step instructions
  - Both shared hosting and VPS deployment options
  - Database configuration (MySQL/PostgreSQL)
  - Static files and media handling
  - SSL/HTTPS setup
  - Security best practices
  - Troubleshooting and maintenance
  
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** ✅ Checklist
  - Track your deployment progress
  - Ensure nothing is missed
  - Quick command reference

---

## 📖 Documentation

### Complete User Journeys
Comprehensive testing documentation for all user flows:

- **[CUSTOMER_JOURNEY.md](CUSTOMER_JOURNEY.md)** 📄
  - Complete customer lifecycle from registration to order management
  - 50+ test checkpoints covering all customer features
  - Registration, profile management, shopping, checkout, and order tracking
  - **Time to read:** 15 minutes | **Test time:** 45 minutes

- **[AGENT_JOURNEY.md](AGENT_JOURNEY.md)** 📄
  - Complete agent/supplier workflow
  - 60+ test checkpoints for all agent features
  - Dashboard, product management, order fulfillment, and delivery management
  - **Time to read:** 20 minutes | **Test time:** 45 minutes

### Testing & Issues
- **[TESTING_SUMMARY.md](TESTING_SUMMARY.md)** - Testing methodology, setup guide, and checklists
- **[ISSUES_FOUND.md](ISSUES_FOUND.md)** - Known issues with detailed reproduction steps (10 issues tracked)
- **[TESTING_EXECUTION_SUMMARY.md](TESTING_EXECUTION_SUMMARY.md)** - Executive summary of all deliverables

---

## 🏗️ Project Structure

```
bhrikutimandap/
├── market/                 # Django project settings
│   ├── settings.py         # Main configuration
│   ├── urls.py             # URL routing
│   └── wsgi.py             # WSGI configuration
├── store/                  # Main Django app
│   ├── models.py           # Database models (User, Product, Order, etc.)
│   ├── views.py            # Customer views
│   ├── agent_views.py      # Agent/supplier views
│   ├── admin.py            # Admin customization (20+ ModelAdmin classes)
│   ├── urls.py             # Customer URL patterns
│   ├── agent_urls.py       # Agent URL patterns
│   ├── forms.py            # Django forms
│   └── management/
│       └── commands/       # Custom management commands
├── templates/              # HTML templates
│   ├── store/              # Customer portal templates
│   ├── agent/              # Agent portal templates
│   └── admin/              # Admin customization
├── static/                 # CSS, JavaScript, images
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   └── img/                # Images
├── media/                  # User-uploaded files
├── db.sqlite3              # SQLite database
├── manage.py               # Django CLI
└── requirements.txt        # Python dependencies
```

---

## 🗄️ Database Models

### Core Models
- **User** - Extended Django user with role management (Customer/Agent)
- **Product** - Product catalog with pricing and inventory
- **Order** - Customer orders with multiple items
- **OrderItem** - Individual items in an order
- **Cart** - Shopping cart management
- **Wishlist** - User's wishlist items

### Agent Models
- **AgentProfile** - Agent/supplier profile information
- **DeliveryPartner** - Delivery partner details (name, contact, email)
- **Vehicle** - Delivery vehicles (type, number, capacity, insurance)
- **OrderDelivery** - Delivery assignment and tracking

### Supporting Models
- **Address** - Shipping and billing addresses
- **PaymentMethod** - Stored payment methods
- **SiteSettings** - Platform-wide settings
- **StockAlert** - Low stock notifications
- **SalesTransaction** - Sales records
- **ReturnRequest** - Customer returns management

---

## 🎯 Main Features Explained

### 1. Role-Based Access Control
- **Customers**: Browse, search, add to cart, checkout, manage orders
- **Agents**: Manage products, handle orders, assign delivery, track shipments
- **Admin**: Full control over all aspects of the platform

### 2. Advanced Search & Filtering
- Search products by name
- Filter by price range
- Filter by supplier/agent
- Combine multiple filters

### 3. Shopping Cart
- Add/remove products
- Adjust quantities
- Real-time price calculation
- Persistent storage across sessions

### 4. Checkout Process
- Multi-step checkout
- Address selection/creation
- Payment method selection/creation
- Order confirmation

### 5. Order Management
- Order history with status tracking
- Detailed order information
- Real-time delivery tracking
- Delivery timeline visualization
- Return request capability

### 6. Delivery Management
- Create and manage delivery partners
- Add multiple vehicles per partner
- Assign specific vehicles to orders
- Track delivery in real-time
- Update delivery status (In Transit → Out for Delivery → Delivered)
- Display delivery timeline to customers

### 7. Agent Dashboard
- Real-time sales metrics
- Revenue tracking
- Order management
- Stock monitoring
- Low stock alerts
- Market insights and suggestions

### 8. Admin Customization
- Custom admin styling
- Enhanced change lists
- Inline editing for related objects
- Advanced filtering and search
- 20+ custom ModelAdmin classes

---

## 🔐 Security Features

- User authentication and authorization
- Password hashing
- CSRF protection
- SQL injection prevention
- XSS protection
- Secure session management
- Role-based access control
- Payment data masking

---

## 🐛 Known Issues & Testing

### Issue #1: ✅ FIXED
**Search Anchor Navigation**
- Fixed scroll position when clicking search icon
- Now scrolls to search section instead of trending products

### Pending Testing
For detailed list of identified issues and testing procedures, see:
- [ISSUES_FOUND.md](ISSUES_FOUND.md) - 10 issues with detailed testing steps

---

## 📊 Technology Stack

### Backend
- **Django 5.2.5** - Web framework
- **Python 3.11** - Programming language
- **SQLite** - Database

### Frontend
- **Bootstrap 4/5** - CSS framework
- **jQuery** - JavaScript library
- **Chart.js** - Data visualization
- **Font Awesome** - Icons
- **Owl Carousel** - Image carousel

### Additional Libraries
- **django-taggit** - Tags (if used)
- **Pillow** - Image processing
- **requests** - HTTP library

---

## 📈 API Endpoints

### Customer Endpoints
```
GET     /                           - Home page
GET     /products/                  - Product list
GET     /product/<id>/              - Product detail
POST    /cart/add/<id>/             - Add to cart
GET     /checkout/                  - Checkout page
POST    /checkout/                  - Place order
GET     /customer/dashboard/        - Customer dashboard
GET     /customer/orders/           - Order history
GET     /order/<id>/                - Order details
POST    /accounts/register/         - Register
POST    /accounts/login/            - Login
POST    /accounts/logout/           - Logout
```

### Agent Endpoints
```
GET     /agent/dashboard/           - Agent dashboard
GET     /agent/products/            - Product list
POST    /agent/product/add/         - Create product
GET     /agent/orders/              - All orders
GET     /agent/orders/incoming/     - Incoming orders
GET     /agent/orders/<id>/         - Order detail
POST    /agent/orders/<id>/assign-delivery/  - Assign delivery
GET     /agent/stock/               - Stock overview
GET     /agent/sales/               - Sales list
GET     /agent/reports/             - Reports
GET     /agent/delivery-partners/   - Delivery partners
```

---

## 🧪 Testing

### Complete Testing Documentation
Follow these comprehensive guides for thorough testing:

1. **[CUSTOMER_JOURNEY.md](CUSTOMER_JOURNEY.md)** - Test complete customer flow
   - Registration through order management
   - 50+ test checkpoints

2. **[AGENT_JOURNEY.md](AGENT_JOURNEY.md)** - Test complete agent operations
   - Dashboard through delivery management
   - 60+ test checkpoints

3. **[ISSUES_FOUND.md](ISSUES_FOUND.md)** - Test identified issues
   - 10 issues with detailed testing steps
   - Clear reproduction paths for each

### Quick Test
```bash
# Run Django system check
python manage.py check

# Run migrations
python manage.py migrate

# Create test data
python manage.py seed

# Start server
python manage.py runserver 8000
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👥 Support & Contact

For issues, questions, or suggestions:
- Create an issue on GitHub
- Review documentation in [CUSTOMER_JOURNEY.md](CUSTOMER_JOURNEY.md) and [AGENT_JOURNEY.md](AGENT_JOURNEY.md)
- Check [TESTING_SUMMARY.md](TESTING_SUMMARY.md) for testing guidance

---

## 📅 Recent Updates

### Latest Changes
- ✅ Complete customer journey documentation (50+ test cases)
- ✅ Complete agent journey documentation (60+ test cases)
- ✅ Fixed search anchor navigation issue
- ✅ Comprehensive issue tracker (10 issues)
- ✅ Testing methodology and guides
- ✅ Delivery management with vehicle assignment

### Upcoming
- Mobile app support
- Advanced analytics
- AI-powered recommendations
- Payment gateway integration
- Email notifications

---

## 🎉 Quick Start Guide

```bash
# 1. Clone and setup
git clone https://github.com/krishnadhakal03/bhrikutimandap.git
cd bhrikutimandap
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2. Setup database
python manage.py migrate
python manage.py createsuperuser
python manage.py seed

# 3. Start server
python manage.py runserver 8000

# 4. Access
Browser: http://localhost:8000
Admin: http://localhost:8000/admin/
Agent: http://localhost:8000/agent/dashboard/

# 5. Test
Follow: CUSTOMER_JOURNEY.md and AGENT_JOURNEY.md
```

---

**Made with ❤️ by Bhrikutimandap Team**  
**Last Updated:** December 21, 2025  
**Version:** 1.0.0
