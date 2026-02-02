from django.core.management.base import BaseCommand
from django.utils import timezone
from documentation.models import AppVersion


class Command(BaseCommand):
    help = 'Seed initial app versions for ShopEase'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING('Seeding App Versions...'))

        # Create v1.0.0 - Initial Release
        version_1_0_0, created = AppVersion.objects.get_or_create(
            version_number='1.0.0',
            defaults={
                'version_type': 'major',
                'is_current_version': True,
                'release_date': timezone.now(),
                'release_notes': '''# ShopEase v1.0.0 - Initial Release

## Features
- Complete e-commerce platform with shopping cart functionality
- Admin panel for product and order management
- User authentication and profile management
- MySQL database integration for data persistence
- Responsive Bootstrap 5.3 UI for optimal viewing across devices
- Production deployment with Nginx + Gunicorn
- Path-based routing for Admin Portal and Documentation portals
- Customer portal with product browsing and ordering
- Secure payment processing integration
- Order tracking and management system

## Technical Stack
- Django 5.1 - Web framework
- MySQL 8.0 - Database
- Bootstrap 5.3 - Frontend framework
- Nginx - Reverse proxy and static file serving
- Gunicorn - WSGI HTTP server
- Redis - Caching layer
- Python 3.12 - Programming language

## Database Models
- User management (Customer, Admin)
- Product catalog with categories
- Shopping cart and order processing
- Reviews and ratings system

## Security Features
- CSRF protection on all forms
- Password hashing with Django's built-in authentication
- Secure session management
- XSS protection

## Deployment
- Development mode: Django runserver
- Production mode: Nginx + Gunicorn
- Ngrok integration for public tunneling
- Static and media file serving optimized for production
'''.strip(),
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created version {version_1_0_0.version_number}'))
        else:
            self.stdout.write(self.style.WARNING(f'Version {version_1_0_0.version_number} already exists'))

        # Create v1.1.0 - Documentation System
        version_1_1_0, created = AppVersion.objects.get_or_create(
            version_number='1.1.0',
            defaults={
                'version_type': 'minor',
                'is_current_version': False,
                'release_date': timezone.now(),
                'release_notes': '''# ShopEase v1.1.0 - Documentation System

## New Features
- ShopEaseDocs project - dedicated documentation portal
- Code explanation system for learning Django codebase
- FAQ management system
- Help center for common issues
- Developer discussion chat system
- Learning progress tracking
- Code quizzes and assessments
- REST API for documentation access

## Enhancements
- Dark mode toggle for better UX
- Search autocomplete functionality
- Breadcrumb navigation
- Mobile-responsive design improvements
- Static file fingerprinting for better caching
- Rate limiting with django-axes for brute-force protection

## Technical Improvements
- Django REST Framework integration
- Markdown rendering with Pygments syntax highlighting
- Context processors for learning progress
- Template tag library for custom filters
- Management commands for data seeding
- Shared database authentication with main app

## Bug Fixes
- Fixed logout 405 error (changed from GET to POST)
- Fixed missing context variables in dev chat view
- Fixed versions page 500 error
- Improved permission system for admin access
'''.strip(),
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created version {version_1_1_0.version_number}'))
        else:
            self.stdout.write(self.style.WARNING(f'Version {version_1_1_0.version_number} already exists'))

        # Summary
        total_versions = AppVersion.objects.count()
        current = AppVersion.objects.filter(is_current_version=True).first()

        self.stdout.write(self.style.MIGRATE_HEADING('\n=== Seeding Complete ==='))
        self.stdout.write(f'Total versions in database: {total_versions}')
        if current:
            self.stdout.write(f'Current version: {current.version_number}')
        self.stdout.write(self.style.SUCCESS('\n✓ Version seeding completed successfully!'))
