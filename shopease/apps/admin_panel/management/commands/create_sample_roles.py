"""
Management command to create sample custom roles for testing the permission system.

Usage:
    python manage.py create_sample_roles [--settings=config.settings.admin]

This command creates sample staff users with custom roles to demonstrate the
permission system. Each user is created with a custom role having specific permissions.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.admin_panel.models import AdminRole


class Command(BaseCommand):
    help = 'Creates sample staff users with custom roles for testing the permission system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete existing sample users and custom roles before creating new ones',
        )

    def handle(self, *args, **options):
        # Sample user prefix to identify demo accounts
        SAMPLE_USER_PREFIX = 'demo_'

        # Clear existing sample users and custom roles if requested
        if options['clear']:
            sample_users = User.objects.filter(username__startswith=SAMPLE_USER_PREFIX)
            deleted_count = sample_users.count()
            sample_users.delete()
            self.stdout.write(
                self.style.WARNING(f'Deleted {deleted_count} existing sample users and their roles')
            )

        # Sample staff users with custom roles
        # Each user has a different custom role with specific permissions
        sample_users = [
            {
                'username': f'{SAMPLE_USER_PREFIX}inventory',
                'email': 'inventory.analyst@shopease.demo',
                'first_name': 'Inventory',
                'last_name': 'Analyst',
                'role_name': 'Inventory Analyst',
                'role_description': 'Can view products and analytics data. Read-only access to inventory and reports.',
                'permissions': {
                    'can_view_products': True,
                    'can_view_analytics': True,
                    'can_export_data': True,
                }
            },
            {
                'username': f'{SAMPLE_USER_PREFIX}orders',
                'email': 'order.manager@shopease.demo',
                'first_name': 'Order',
                'last_name': 'Manager',
                'role_name': 'Order Manager',
                'role_description': 'Can view, edit, and manage customer orders. Can process refunds.',
                'permissions': {
                    'can_view_orders': True,
                    'can_edit_orders': True,
                    'can_process_refunds': True,
                }
            },
            {
                'username': f'{SAMPLE_USER_PREFIX}content',
                'email': 'content.moderator@shopease.demo',
                'first_name': 'Content',
                'last_name': 'Moderator',
                'role_name': 'Content Moderator',
                'role_description': 'Can moderate product reviews and manage featured products.',
                'permissions': {
                    'can_moderate_reviews': True,
                    'can_manage_featured': True,
                    'can_view_products': True,
                }
            },
            {
                'username': f'{SAMPLE_USER_PREFIX}sales',
                'email': 'sales.analyst@shopease.demo',
                'first_name': 'Sales',
                'last_name': 'Analyst',
                'role_name': 'Sales Analyst',
                'role_description': 'Can view orders, products, and analytics. Can export data for reports.',
                'permissions': {
                    'can_view_orders': True,
                    'can_view_products': True,
                    'can_view_analytics': True,
                    'can_export_data': True,
                }
            },
            {
                'username': f'{SAMPLE_USER_PREFIX}product',
                'email': 'product.manager@shopease.demo',
                'first_name': 'Product',
                'last_name': 'Manager',
                'role_name': 'Product Manager',
                'role_description': 'Full control over products and featured items. Can edit products and manage featured products.',
                'permissions': {
                    'can_view_products': True,
                    'can_edit_products': True,
                    'can_manage_featured': True,
                    'can_view_analytics': True,
                }
            },
            {
                'username': f'{SAMPLE_USER_PREFIX}support',
                'email': 'support.lead@shopease.demo',
                'first_name': 'Support',
                'last_name': 'Lead',
                'role_name': 'Customer Support Lead',
                'role_description': 'Can view users, moderate reviews, and manage customer orders.',
                'permissions': {
                    'can_view_users': True,
                    'can_view_orders': True,
                    'can_edit_orders': True,
                    'can_moderate_reviews': True,
                }
            },
        ]

        created_count = 0
        DEFAULT_PASSWORD = 'shopease2025'

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Creating sample staff users with custom roles...'))
        self.stdout.write('')

        for user_data in sample_users:
            # Check if user already exists
            if User.objects.filter(username=user_data['username']).exists():
                self.stdout.write(
                    self.style.WARNING(f'  User "{user_data["username"]}" already exists. Skipping...')
                )
                continue

            # Create staff user
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=DEFAULT_PASSWORD,
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                is_staff=True,
                is_active=True,
            )

            # Create custom role for this user
            role = AdminRole.objects.create(
                user=user,
                is_custom_role=True,
                custom_role_name=user_data['role_name'],
                role_description=user_data['role_description'],
                role='',  # Empty since it's a custom role
                **user_data['permissions']
            )

            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'  [OK] Created user: {user_data["username"]}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'    Name: {user_data["first_name"]} {user_data["last_name"]}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'    Email: {user_data["email"]}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'    Role: {user_data["role_name"]}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'    Description: {user_data["role_description"]}')
            )

            # Show permissions
            permissions = [perm for perm, value in user_data['permissions'].items() if value]
            self.stdout.write(
                self.style.SUCCESS(f'    Permissions: {", ".join(permissions)}')
            )
            self.stdout.write('')  # Empty line for readability

        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample staff users with custom roles!')
        )
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('IMPORTANT: Default password for all demo users'))
        self.stdout.write(self.style.WARNING(f'Password: {DEFAULT_PASSWORD}'))
        self.stdout.write('')
        self.stdout.write('Login to the Admin Panel (http://localhost:8080) with any of these users:')
        for user_data in sample_users:
            self.stdout.write(f'  - {user_data["username"]} ({user_data["role_name"]})')
        self.stdout.write('')
        self.stdout.write('Each user has different permissions to demonstrate the role system.')
        self.stdout.write('')
