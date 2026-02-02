# ShopEase Documentation System

A comprehensive documentation project for the ShopEase e-commerce platform, running as a separate Django project within the same repository.

## Overview

This is a standalone Django project that shares the same database with ShopEase, providing:
- **Public Documentation**: Help articles, FAQs, and guides for all users
- **Code Explanations**: Detailed code-level documentation (superuser-only)
- **Developer Chat**: WhatsApp-like discussion system for developers
- **Version Tracking**: App versions and release notes
- **Daily Issue Help**: Common problems and solutions

## Server Configuration

- **Documentation Server**: Port **9000** (http://127.0.0.1:9000)
- **ShopEase Customer Server**: Port 8000
- **ShopEase Admin Server**: Port 8080

## Features

### 1. **Authentication Integration**
- Uses same MySQL database as ShopEase
- Shares user authentication (same login credentials)
- Respects ShopEase AdminRole permissions

### 2. **8 Core Models**
- **DocCategory**: Organize documentation by categories
- **Documentation**: Main documentation articles with audience targeting
- **CodeExplanation**: Superuser-only code explanations for learning
- **FAQ**: Frequently asked questions
- **DeveloperDiscussion**: Discussion threads (WhatsApp-like)
- **DeveloperMessage**: Chat messages
- **AppVersion**: Version tracking and release notes
- **DailyIssueHelp**: Common day-to-day issues and solutions

### 3. **Audience Targeting**
- **ALL**: Visible to everyone (customers and admins)
- **CUSTOMER**: Customers only
- **ADMIN**: Admin users only
- **SUPERUSER**: Superusers only (for code explanations)

### 4. **DEVELOPER Role**
New role added to ShopEase admin panel with permissions:
- View/Edit documentation
- Manage FAQs
- Participate in developer chat
- View analytics
- View products and orders

## Installation & Setup

### 1. Database Configuration
The project uses the same `.env` file as ShopEase with database credentials:
```
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=3306
```

### 2. Run Migrations
Migrations have already been applied, but if you need to rerun:
```bash
cd shopeasedocs
python manage.py migrate
```

### 3. Start the Server

**Option 1: Using the batch script (Windows)**
```bash
run_docs_server.bat
```

**Option 2: Manual command**
```bash
python manage.py runserver 9000
```

The documentation server will be available at: **http://127.0.0.1:9000**

### 4. Access Django Admin
Create a superuser if needed:
```bash
python manage.py createsuperuser
```

Access admin panel at: **http://127.0.0.1:9000/admin**

## Project Structure

```
shopeasedocs/
├── manage.py
├── run_docs_server.bat          # Convenience script to run server
├── .env                          # Database configuration (shared with shopease)
├── shopeasedocs/                 # Project configuration
│   ├── settings.py              # Django settings
│   ├── urls.py                  # URL routing
│   └── wsgi.py                  # WSGI config
├── documentation/                # Main app
│   ├── models.py                # 8 core models
│   ├── views.py                 # View logic
│   ├── urls.py                  # App URL patterns
│   ├── forms.py                 # Django forms
│   ├── admin.py                 # Django admin config
│   └── migrations/              # Database migrations
├── templates/
│   └── documentation/
│       ├── public/              # Customer-facing templates
│       ├── admin/               # Admin management templates
│       ├── code/                # Code explanation templates
│       └── dev_chat/            # Developer chat templates
└── static/
    └── documentation/
        ├── css/                 # External CSS files
        └── js/                  # External JavaScript files
```

## ShopEase Integration

### AdminRole Model Updates
The ShopEase `AdminRole` model has been extended with 6 new permissions:
- `can_view_documentation`: Can view documentation admin panel
- `can_edit_documentation`: Can create/edit documentation
- `can_manage_faqs`: Can manage FAQ entries
- `can_access_code_docs`: Can view code-level explanations (superuser only)
- `can_participate_dev_chat`: Can participate in developer discussions
- `can_manage_versions`: Can manage app versions and release notes

### DEVELOPER Role Permissions
The new DEVELOPER role includes:
- Documentation: View and Edit
- FAQs: Manage
- Developer Chat: Participate
- Analytics: View
- Products: View
- Orders: View

## Development Workflow

### Running Both Projects Simultaneously

1. **Terminal 1** - ShopEase Customer Server (port 8000):
   ```bash
   cd shopease
   python manage.py runserver 8000
   ```

2. **Terminal 2** - ShopEase Admin Server (port 8080):
   ```bash
   cd shopease
   set DJANGO_SETTINGS_MODULE=config.settings.admin
   python manage.py runserver 8080
   ```

3. **Terminal 3** - Documentation Server (port 9000):
   ```bash
   cd shopeasedocs
   python manage.py runserver 9000
   ```

### Creating Sample Data

Use Django admin to create:
1. **Categories**: Create doc categories (Getting Started, API Reference, etc.)
2. **Documentation**: Add documentation articles
3. **FAQs**: Add frequently asked questions
4. **Code Explanations**: Add code explanations (superuser-only)
5. **App Versions**: Track ShopEase versions
6. **Daily Help**: Add common issue solutions

## Next Steps (Implementation TODO)

- [ ] Create forms for all models
- [ ] Implement URL routing
- [ ] Create views (public, admin, code, chat)
- [ ] Design and implement templates
- [ ] Add external CSS styling
- [ ] Add external JavaScript functionality
- [ ] Implement search functionality
- [ ] Add "Was this helpful?" feature
- [ ] Implement developer chat AJAX polling
- [ ] Add Markdown rendering support
- [ ] Add syntax highlighting for code
- [ ] Create navigation integration

## Technology Stack

- **Backend**: Django 5.2.4, Python 3.13
- **Database**: MySQL (shared with ShopEase)
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Markdown**: SimpleMDE/EasyMDE (planned)
- **Rich Editor**: TinyMCE/CKEditor (planned)
- **Syntax Highlighting**: Prism.js (planned)
- **Charts**: Chart.js (planned)

## Security Notes

- Code explanations are **strictly** superuser-only (enforced in views)
- Developer chat requires `can_participate_dev_chat` permission
- All admin actions are permission-gated
- Uses same authentication as ShopEase (secure, tested)
- CSRF protection enabled
- Session management shared with ShopEase

## Contributing

This documentation system is designed to be:
- Easy to extend with new documentation types
- Flexible with audience targeting
- Integrated with ShopEase permissions
- Scalable for future features

---

**Documentation Server**: http://127.0.0.1:9000
**ShopEase Customer**: http://127.0.0.1:8000
**ShopEase Admin**: http://127.0.0.1:8080
