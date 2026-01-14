# ShopEase Admin Panel Documentation

A comprehensive custom admin panel for ShopEase e-commerce platform built with Django 5.0.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation & Setup](#installation--setup)
- [User Roles & Permissions](#user-roles--permissions)
- [Modules](#modules)
  - [Dashboard](#1-dashboard)
  - [Order Management](#2-order-management)
  - [Product Analytics](#3-product-analytics)
  - [Featured Products](#4-featured-products)
  - [Review Management](#5-review-management)
  - [User Management](#6-user-management)
  - [Reports & Analytics](#7-reports--analytics)
- [API Endpoints](#api-endpoints)
- [Management Commands](#management-commands)
- [File Structure](#file-structure)
- [Customization](#customization)

---

## Overview

The ShopEase Admin Panel is a custom-built administrative interface located at `/dashboard/`. It provides role-based access control, comprehensive order management, product analytics, review moderation, user management, and detailed reporting.

**URL**: `http://localhost:8000/dashboard/`

**Requirements**:
- Django 5.0+
- MySQL Database
- WeasyPrint (for PDF invoices)
- Bootstrap 5 (included via CDN)
- Chart.js (included via CDN)

---

## Features

| Feature | Description |
|---------|-------------|
| Role-Based Access | 5 admin roles with granular permissions |
| Order Management | Full order lifecycle, refunds, PDF invoices |
| Product Analytics | View tracking, engagement metrics, featured scoring |
| Review Moderation | Approve/reject reviews, bulk actions |
| User Management | Staff creation, role assignment, activity logs |
| Reports | Sales, revenue, product performance with CSV export |
| Email Automation | Automatic order status emails |
| Activity Logging | Complete audit trail of admin actions |

---

## Installation & Setup

### 1. Add to Installed Apps

```python
# config/settings.py
INSTALLED_APPS = [
    ...
    'apps.admin_panel',
]
```

### 2. Add Middleware

```python
# config/settings.py
MIDDLEWARE = [
    ...
    'apps.admin_panel.middleware.ProductViewTrackingMiddleware',
]
```

### 3. Add Context Processor

```python
# config/settings.py
TEMPLATES = [
    {
        ...
        'OPTIONS': {
            'context_processors': [
                ...
                'apps.admin_panel.context_processors.admin_permissions',
            ],
        },
    },
]
```

### 4. Add URL Pattern

```python
# config/urls.py
urlpatterns = [
    ...
    path('dashboard/', include('apps.admin_panel.urls', namespace='admin_panel')),
]
```

### 5. Run Migrations

```bash
python manage.py makemigrations admin_panel
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 7. Install WeasyPrint (for PDF invoices)

```bash
pip install weasyprint==60.2
```

---

## User Roles & Permissions

### Available Roles

| Role | Description |
|------|-------------|
| `SUPER_ADMIN` | Full access to all features |
| `ORDER_MANAGER` | Manage orders, process refunds |
| `INVENTORY_MANAGER` | Manage products and inventory |
| `MARKETING_MANAGER` | Manage featured products, analytics |
| `CUSTOMER_SERVICE` | View orders, moderate reviews |

### Permission Matrix

| Permission | Super Admin | Order Manager | Inventory Manager | Marketing Manager | Customer Service |
|------------|:-----------:|:-------------:|:-----------------:|:-----------------:|:----------------:|
| View Orders | ✅ | ✅ | ❌ | ❌ | ✅ |
| Edit Orders | ✅ | ✅ | ❌ | ❌ | ❌ |
| Process Refunds | ✅ | ✅ | ❌ | ❌ | ❌ |
| View Products | ✅ | ❌ | ✅ | ✅ | ❌ |
| Edit Products | ✅ | ❌ | ✅ | ❌ | ❌ |
| Manage Inventory | ✅ | ❌ | ✅ | ❌ | ❌ |
| Moderate Reviews | ✅ | ❌ | ❌ | ❌ | ✅ |
| Manage Featured | ✅ | ❌ | ❌ | ✅ | ❌ |
| View Users | ✅ | ❌ | ❌ | ❌ | ❌ |
| Edit Users | ✅ | ❌ | ❌ | ❌ | ❌ |
| View Analytics | ✅ | ❌ | ✅ | ✅ | ❌ |
| View Activity | ✅ | ❌ | ❌ | ❌ | ❌ |

### Assigning Roles

1. Navigate to **Users** in the sidebar
2. Click on a user to view their profile
3. Click **Assign Role** or **Edit Role**
4. Select the desired role
5. Click **Save**

---

## Modules

### 1. Dashboard

**URL**: `/dashboard/`

The main dashboard provides an overview of key metrics:

- Today's orders and revenue
- Pending orders count
- Low stock alerts
- Recent orders list
- Quick stats (total customers, products, revenue)

### 2. Order Management

**URL**: `/dashboard/orders/`

#### Features:
- View all orders with filtering (status, date, search)
- Order detail view with full information
- Update order status (Pending → Processing → Shipped → Delivered → Completed)
- Generate PDF invoices
- Process refunds with stock restoration
- Bulk status updates
- Automatic email notifications on status change

#### Order Statuses:
```
PENDING → PROCESSING → SHIPPED → DELIVERED → COMPLETED
                                          ↘ CANCELLED
```

#### Refund Process:
1. Go to Order Detail
2. Click "Process Refund"
3. Enter refund amount and reason
4. Choose whether to restore stock
5. Submit refund request

### 3. Product Analytics

**URL**: `/dashboard/products/`

#### Features:
- View all products with analytics metrics
- Filter by category, date range, sort by various metrics
- Detailed product analytics with charts:
  - Views over time
  - Purchases over time
  - Revenue trends
  - Featured score history

#### Metrics Tracked:
- Page views (total and unique)
- Cart additions
- Wishlist additions
- Purchases
- Revenue
- Average rating
- Review count
- Featured score

#### Featured Score Formula:
```
Score = Revenue (40%) + Purchases (20%) + Engagement (15%) +
        Views (10%) + Rating (10%) + Reviews (5%)
```

### 4. Featured Products

**URL**: `/dashboard/products/featured/dashboard/`

#### Features:
- View top products by featured score
- See currently featured products performance
- Trending products (biggest score increase)
- Manual product featuring
- Auto-suggested products based on analytics
- Set priority and expiry dates

#### Managing Featured Products:
1. Go to **Featured Products** → **Manage**
2. View auto-suggestions on the right
3. Click "Add to Featured" for auto-suggested products
4. Or manually select a product from dropdown
5. Set priority (lower = higher position)
6. Optionally set expiry date

### 5. Review Management

**URL**: `/dashboard/reviews/`

#### Features:
- View all reviews with filtering
- Pending reviews queue for quick moderation
- Approve/reject individual reviews
- Bulk approve/reject/delete
- Review analytics dashboard
- View reviewer history

#### Moderation Workflow:
1. Go to **Reviews** → **Pending**
2. Review each submission
3. Click **Approve** or **Reject**
4. Or select multiple and use bulk actions

#### Review Analytics:
- Total reviews, pending, approved counts
- Average rating
- Rating distribution chart
- Reviews over time chart
- Top reviewed products
- Top rated products

### 6. User Management

**URL**: `/dashboard/users/`

#### Features:
- View all users (staff and customers)
- Filter by type, role, status
- User detail view with:
  - Profile information
  - Order history
  - Review activity
  - Admin activity (for staff)
- Assign/remove admin roles
- Activate/deactivate accounts
- Create new staff users
- Activity log viewer

#### Creating Staff Users:
1. Go to **Users**
2. Click **New Staff**
3. Fill in username, email, password
4. Select admin role
5. Click **Create Staff User**

#### Activity Log:
**URL**: `/dashboard/activity/`

View all admin actions with:
- Timestamp
- User who performed action
- Action type
- Description
- IP address

### 7. Reports & Analytics

**URL**: `/dashboard/reports/`

#### Available Reports:

##### Sales Report (`/dashboard/reports/sales/`)
- Date range filtering
- Key metrics (orders, revenue, AOV)
- Daily sales chart
- Top products by revenue
- Top products by quantity
- Payment method breakdown
- CSV export

##### Revenue Analytics (`/dashboard/reports/revenue/`)
- Monthly revenue trends
- Revenue by category
- Growth rate vs previous period
- Monthly comparison chart

##### Product Performance (`/dashboard/reports/products/`)
- Best selling products
- Low stock alerts
- Out of stock products
- Products with no sales
- Top rated products
- Low rated products
- CSV export

#### CSV Export:
Click the **Export CSV** button on any report to download data.

---

## API Endpoints

### Featured Products Auto-Suggest

```
GET /dashboard/products/featured/auto-suggest/
```

**Parameters:**
- `days` (int): Number of days to analyze (default: 7)
- `limit` (int): Number of suggestions (default: 10)

**Response:**
```json
{
  "success": true,
  "suggestions": [
    {
      "id": 1,
      "name": "Product Name",
      "sku": "SKU123",
      "price": 999.00,
      "stock": 50,
      "featured_score": 85.5,
      "revenue": 15000.00,
      "purchases": 25,
      "views": 500,
      "image_url": "/media/products/image.jpg"
    }
  ],
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-01-07"
  }
}
```

---

## Management Commands

### Aggregate Analytics

Aggregates daily product analytics for featured product scoring.

```bash
# Run for yesterday (default)
python manage.py aggregate_analytics

# Run for specific date
python manage.py aggregate_analytics --date 2024-01-15

# Run for date range
python manage.py aggregate_analytics --start-date 2024-01-01 --end-date 2024-01-31
```

**Schedule this command daily** (e.g., via cron at 2 AM):
```bash
0 2 * * * cd /path/to/shopease && python manage.py aggregate_analytics
```

---

## File Structure

```
apps/admin_panel/
├── __init__.py
├── admin.py                    # Django admin registration
├── apps.py                     # App configuration
├── context_processors.py       # Template context processors
├── decorators.py               # Permission decorators
├── middleware.py               # Product view tracking
├── models.py                   # AdminRole, AdminActivity, Refund, Analytics models
├── signals.py                  # Email automation, engagement tracking
├── urls.py                     # URL patterns
├── README.md                   # This documentation
│
├── management/
│   └── commands/
│       └── aggregate_analytics.py   # Daily analytics command
│
├── migrations/                 # Database migrations
│
├── utils/
│   └── pdf_generator.py        # Invoice PDF generation
│
└── views/
    ├── __init__.py
    ├── dashboard.py            # Dashboard view
    ├── orders.py               # Order management views
    ├── products.py             # Product analytics views
    ├── reviews.py              # Review moderation views
    ├── users.py                # User management views
    └── reports.py              # Reports & analytics views

templates/admin_panel/
├── base_admin.html             # Base template with sidebar
├── dashboard.html              # Dashboard template
│
├── orders/
│   ├── list.html               # Order list
│   ├── detail.html             # Order detail
│   └── invoice_pdf.html        # PDF invoice template
│
├── products/
│   ├── analytics_list.html     # Product analytics list
│   ├── analytics_detail.html   # Product analytics detail
│   ├── featured_dashboard.html # Featured products dashboard
│   └── manage_featured.html    # Manage featured products
│
├── reviews/
│   ├── list.html               # Review list
│   ├── pending.html            # Pending reviews queue
│   ├── detail.html             # Review detail
│   └── analytics.html          # Review analytics
│
├── users/
│   ├── list.html               # User list
│   ├── detail.html             # User detail
│   ├── staff_list.html         # Staff list
│   ├── assign_role.html        # Assign role form
│   ├── create_staff.html       # Create staff form
│   └── activity_log.html       # Activity log
│
├── reports/
│   ├── dashboard_overview.html # Reports dashboard
│   ├── sales.html              # Sales report
│   ├── revenue.html            # Revenue analytics
│   └── product_performance.html # Product performance
│
└── emails/
    ├── order_status_change.html # Order status email (HTML)
    └── order_status_change.txt  # Order status email (Plain text)

static/admin_panel/
└── css/
    └── admin.css               # Custom admin styles
```

---

## Customization

### Adding New Permissions

1. Add field to `AdminRole` model:
```python
# models.py
can_new_permission = models.BooleanField(default=False)
```

2. Update `get_default_permissions()` method in `AdminRole`

3. Add to context processor:
```python
# context_processors.py
'can_new_permission': admin_role.can_new_permission,
```

4. Use in templates:
```html
{% if user_permissions.can_new_permission %}
    <!-- Show content -->
{% endif %}
```

5. Use in views:
```python
@permission_required('can_new_permission')
def my_view(request):
    ...
```

### Adding New Admin Roles

1. Add to `ROLE_CHOICES` in `AdminRole` model
2. Update `get_default_permissions()` with default permissions for new role

### Customizing Email Templates

Edit templates in `templates/emails/`:
- `order_status_change.html` - HTML version
- `order_status_change.txt` - Plain text version

### Customizing PDF Invoice

Edit `templates/admin_panel/orders/invoice_pdf.html`

Update company info in `utils/pdf_generator.py`:
```python
company_info = {
    'name': 'Your Company',
    'address': '123 Street',
    'city': 'City',
    'phone': '+91 1234567890',
    'email': 'contact@company.com',
    'gst': 'GSTIN123456789'
}
```

---

## Troubleshooting

### Common Issues

**1. Sidebar permissions not showing correctly**
- Ensure context processor is added to settings.py
- Clear browser cache
- Check user has AdminRole assigned

**2. PDF invoice not generating**
- Install WeasyPrint: `pip install weasyprint==60.2`
- On Windows, install GTK3: https://weasyprint.org/start/

**3. Analytics not updating**
- Run: `python manage.py aggregate_analytics`
- Check middleware is added to settings.py
- Verify ProductView records are being created

**4. Emails not sending**
- Check EMAIL settings in settings.py
- For development, emails print to console
- For production, configure SMTP settings

---

## Support

For issues or feature requests, please contact the development team.

---

*Last Updated: January 2025*
*Version: 1.0.0*
