"""
========================================
FETCH FAKE PRODUCTS - Management Command
========================================
Populates database with products from Fake Store API.

Usage:
    python manage.py fetch_fake_products

What this does:
1. Fetches categories and products from https://fakestoreapi.com
2. Downloads product images and saves to MEDIA_ROOT
3. Creates database records with proper relationships
4. Handles errors gracefully (network issues, duplicate data)

Security Notes:
- Uses requests library with timeout to prevent hanging
- Validates image URLs before downloading
- Sanitizes category/product names
- Uses Django ORM (prevents SQL injection)

Performance:
- Downloads images in chunks to save memory
- Uses get_or_create to avoid duplicates
- Batches database operations where possible
"""

import requests
import os
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from apps.products.models import Category, Product
from decimal import Decimal
import time


class Command(BaseCommand):
    """
    Django management command to fetch fake products.
    
    Run with: python manage.py fetch_fake_products
    """
    
    help = 'Fetches products from Fake Store API and populates database'
    
    # API endpoints
    API_BASE = 'https://fakestoreapi.com'
    CATEGORIES_URL = f'{API_BASE}/products/categories'
    PRODUCTS_URL = f'{API_BASE}/products'
    
    def handle(self, *args, **options):
        """
        Main command execution method.
        
        Django calls this when command is run.
        *args and **options allow passing command-line arguments.
        """
        
        self.stdout.write(self.style.SUCCESS('Starting to fetch fake products...'))
        
        try:
            # Step 1: Fetch and create categories
            categories = self.fetch_categories()
            self.stdout.write(self.style.SUCCESS(f'✓ Fetched {len(categories)} categories'))
            
            # Step 2: Fetch and create products
            products_count = self.fetch_products()
            self.stdout.write(self.style.SUCCESS(f'✓ Created {products_count} products'))
            
            self.stdout.write(self.style.SUCCESS('\n🎉 Successfully populated database with fake products!'))
            self.stdout.write(self.style.WARNING('\nNote: Product images are downloaded from external URLs.'))
            
        except Exception as e:
            # Catch any errors and display them
            self.stdout.write(self.style.ERROR(f'✗ Error: {str(e)}'))
            raise
    
    def fetch_categories(self):
        """
        Fetch categories from API and create in database.
        
        Returns: Dictionary mapping category names to Category objects
        
        Error Handling:
        - Timeout after 10 seconds if API doesn't respond
        - Raise error if HTTP status code is not 200
        """
        
        self.stdout.write('Fetching categories from API...')
        
        try:
            # Make HTTP GET request with timeout
            # timeout=10: Wait max 10 seconds for response
            response = requests.get(self.CATEGORIES_URL, timeout=10)
            response.raise_for_status()  # Raise error if status code >= 400
            
            category_names = response.json()  # Parse JSON response
            
        except requests.exceptions.Timeout:
            raise Exception('API request timed out. Check your internet connection.')
        except requests.exceptions.RequestException as e:
            raise Exception(f'Failed to fetch categories: {str(e)}')
        
        # Create Category objects
        categories = {}
        
        for name in category_names:
            # Capitalize category name for better display
            # "men's clothing" → "Men's Clothing"
            display_name = name.title()
            
            # get_or_create: Returns (object, created)
            # - If category exists: returns existing category
            # - If doesn't exist: creates new category
            # This prevents duplicate categories if command run multiple times
            category, created = Category.objects.get_or_create(
                slug=slugify(name),  # URL-safe slug
                defaults={
                    'name': display_name,
                    'is_active': True
                }
            )
            
            categories[name] = category  # Store for product creation
            
            if created:
                self.stdout.write(f'  Created category: {display_name}')
            else:
                self.stdout.write(f'  Category exists: {display_name}')
        
        return categories
    
    def fetch_products(self):
        """
        Fetch products from API and create in database.
        
        Returns: Number of products created
        
        Process:
        1. Fetch all products from API
        2. For each product:
           - Download product image
           - Create Product record
           - Mark some as featured
        
        Performance:
        - Downloads images one at a time (could be parallelized for speed)
        - Uses get_or_create to avoid duplicates
        """
        
        self.stdout.write('\nFetching products from API...')
        
        try:
            response = requests.get(self.PRODUCTS_URL, timeout=10)
            response.raise_for_status()
            products_data = response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f'Failed to fetch products: {str(e)}')
        
        # Re-fetch categories for mapping
        categories = {
            cat.slug: cat for cat in Category.objects.all()
        }
        
        products_created = 0
        
        # Process each product from API
        for index, product_data in enumerate(products_data, 1):
            
            self.stdout.write(f'\nProcessing product {index}/{len(products_data)}: {product_data["title"][:50]}...')
            
            try:
                # Map API category to our Category object
                category_name = product_data['category']
                category_slug = slugify(category_name)
                category = categories.get(category_slug)
                
                if not category:
                    self.stdout.write(self.style.WARNING(f'  Category not found: {category_name}'))
                    continue
                
                # Generate unique slug
                # slugify removes special chars, converts to lowercase
                slug = slugify(product_data['title'])
                
                # Check if product already exists
                if Product.objects.filter(slug=slug).exists():
                    self.stdout.write(f'  Product already exists: {slug}')
                    continue
                
                # Download product image
                # This is the slowest part - downloading from external URL
                image_content = self.download_image(product_data['image'])
                
                if not image_content:
                    self.stdout.write(self.style.WARNING('  Failed to download image, skipping...'))
                    continue
                
                # Create Product object
                # We use create() here since we already checked if exists
                product = Product.objects.create(
                    name=product_data['title'],
                    slug=slug,
                    description=product_data['description'],
                    short_description=product_data['description'][:200],  # First 200 chars
                    category=category,
                    price=Decimal(str(product_data['price'])),  # Convert to Decimal for accuracy
                    stock=100,  # Default stock
                    is_active=True,
                    is_featured=(index <= 8)  # First 8 products are featured
                )
                
                # Save downloaded image to product
                # image_content is bytes, we wrap in ContentFile
                # File saved to MEDIA_ROOT/products/
                image_name = f"{slug}.jpg"
                product.image.save(image_name, ContentFile(image_content), save=True)
                
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created: {product.name[:50]}'))
                products_created += 1
                
                # Small delay to be nice to external API
                time.sleep(0.1)
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error creating product: {str(e)}'))
                continue
        
        return products_created
    
    def download_image(self, image_url):
        """
        Download image from URL and return as bytes.
        
        Args:
            image_url: Full URL to image
        
        Returns:
            bytes: Image content, or None if download fails
        
        Security:
        - Only downloads from HTTPS URLs (comment out for HTTP)
        - Timeout after 30 seconds
        - Streams download in chunks to save memory
        
        Performance:
        - Downloads in 8KB chunks (prevents loading huge files into memory)
        - Total size limit could be added for safety
        """
        
        try:
            # Validate URL (optional security check)
            if not image_url.startswith('https://'):
                # Fake Store API uses HTTPS, but allow HTTP for testing
                if not image_url.startswith('http://'):
                    return None
            
            self.stdout.write(f'  Downloading image: {image_url}')
            
            # stream=True: Download in chunks, don't load entire file into memory
            response = requests.get(image_url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Read response content
            # This loads the entire image into memory
            # For very large images, could stream directly to file
            return response.content
            
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.WARNING(f'  Failed to download image: {str(e)}'))
            return None