from django.core.management.base import BaseCommand
from documentation.models import FAQ, DocCategory


class Command(BaseCommand):
    help = 'Seed FAQ data for ShopEase'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING('Seeding FAQs...'))

        # Create categories
        general_cat, _ = DocCategory.objects.get_or_create(
            slug='general',
            defaults={
                'name': 'General',
                'description': 'General questions about ShopEase',
                'order': 1,
            }
        )

        account_cat, _ = DocCategory.objects.get_or_create(
            slug='account',
            defaults={
                'name': 'Account & Login',
                'description': 'Questions about user accounts and authentication',
                'order': 2,
            }
        )

        orders_cat, _ = DocCategory.objects.get_or_create(
            slug='orders',
            defaults={
                'name': 'Orders & Shipping',
                'description': 'Questions about placing and tracking orders',
                'order': 3,
            }
        )

        payment_cat, _ = DocCategory.objects.get_or_create(
            slug='payment',
            defaults={
                'name': 'Payment & Refunds',
                'description': 'Questions about payments and refund policy',
                'order': 4,
            }
        )

        products_cat, _ = DocCategory.objects.get_or_create(
            slug='products',
            defaults={
                'name': 'Products & Catalog',
                'description': 'Questions about products and browsing',
                'order': 5,
            }
        )

        # FAQ data
        faqs_data = [
            # General category
            {
                'question': 'What is ShopEase?',
                'answer': '''ShopEase is a complete e-commerce platform built with Django, designed to provide a seamless online shopping experience.

It features:
- User-friendly product browsing
- Secure shopping cart and checkout
- Admin panel for store management
- Order tracking and management
- Responsive design for all devices''',
                'category': general_cat,
                'order': 1,
            },
            {
                'question': 'How do I contact customer support?',
                'answer': '''You can contact our customer support team through:

- Help Center: Click on "Help" in the navigation menu
- Email: support@shopease.com
- Developer Chat: For technical discussions (requires admin access)

Our support team typically responds within 24 hours.''',
                'category': general_cat,
                'order': 2,
            },
            {
                'question': 'Is ShopEase available on mobile devices?',
                'answer': '''Yes! ShopEase is fully responsive and works seamlessly on all devices including:

- Smartphones (iOS and Android)
- Tablets
- Desktop computers
- Laptops

Our mobile-optimized interface ensures a great shopping experience on any screen size.''',
                'category': general_cat,
                'order': 3,
            },

            # Account & Login category
            {
                'question': 'How do I create an account?',
                'answer': '''To create an account on ShopEase:

1. Click "Sign Up" in the top right corner
2. Fill in your details (name, email, password)
3. Verify your email address
4. Complete your profile (optional)

Once registered, you can start shopping immediately!''',
                'category': account_cat,
                'order': 1,
            },
            {
                'question': 'How do I reset my password?',
                'answer': '''To reset your password:

1. Navigate to the login page
2. Click "Forgot Password?"
3. Enter your registered email address
4. Check your inbox for a password reset link
5. Click the link and create a new password

The reset link expires after 24 hours for security.''',
                'category': account_cat,
                'order': 2,
            },
            {
                'question': 'Can I change my email address?',
                'answer': '''Yes, you can update your email address:

1. Log into your account
2. Go to "My Profile"
3. Click "Edit Profile"
4. Update your email address
5. Verify the new email through the confirmation link

Note: You'll need to re-verify your new email address.''',
                'category': account_cat,
                'order': 3,
            },
            {
                'question': 'How do I delete my account?',
                'answer': '''To delete your account:

1. Log into your account
2. Go to Account Settings
3. Select "Delete Account"
4. Confirm your decision

**Important:** Account deletion is permanent and cannot be undone. All your order history will be deleted.''',
                'category': account_cat,
                'order': 4,
            },

            # Orders & Shipping category
            {
                'question': 'How do I track my order?',
                'answer': '''To track your order:

1. Log into your account
2. Go to "My Orders"
3. Click on the order you want to track
4. View the current status and tracking information

You'll also receive email updates at each stage of delivery.

**Order Statuses:**
- Pending: Order received, awaiting processing
- Processing: Being prepared for shipment
- Shipped: On its way to you
- Delivered: Successfully delivered''',
                'category': orders_cat,
                'order': 1,
            },
            {
                'question': 'How long does shipping take?',
                'answer': '''Shipping times vary by location:

- Standard Shipping: 5-7 business days
- Express Shipping: 2-3 business days
- Overnight Shipping: 1 business day

Please note that processing time (1-2 business days) is separate from shipping time.''',
                'category': orders_cat,
                'order': 2,
            },
            {
                'question': 'Can I modify or cancel my order?',
                'answer': '''**Before Shipping:**
You can modify or cancel your order by contacting customer support within 2 hours of placing the order.

**After Shipping:**
Once shipped, orders cannot be modified. You can refuse delivery or initiate a return after receiving the item.

To cancel:
1. Go to "My Orders"
2. Select the order
3. Click "Cancel Order" (if available)
4. Confirm cancellation''',
                'category': orders_cat,
                'order': 3,
            },
            {
                'question': 'What if my order arrives damaged?',
                'answer': '''If your order arrives damaged:

1. Take photos of the damage (packaging and product)
2. Contact customer support within 48 hours
3. Provide order number and photos
4. We'll arrange a replacement or refund

**Important:** Keep all original packaging until the issue is resolved.''',
                'category': orders_cat,
                'order': 4,
            },

            # Payment & Refunds category
            {
                'question': 'What payment methods do you accept?',
                'answer': '''We accept the following payment methods:

- Credit Cards (Visa, Mastercard, American Express)
- Debit Cards
- PayPal
- UPI (Unified Payments Interface)
- Net Banking
- Cash on Delivery (select locations)

All transactions are secured with SSL encryption.''',
                'category': payment_cat,
                'order': 1,
            },
            {
                'question': 'Is my payment information secure?',
                'answer': '''Absolutely! We take payment security seriously:

- SSL/TLS encryption for all transactions
- PCI DSS compliant payment processing
- We never store complete credit card information
- Secure payment gateways (Stripe, PayPal)
- Regular security audits

Your payment information is safe with us.''',
                'category': payment_cat,
                'order': 2,
            },
            {
                'question': 'What is your refund policy?',
                'answer': '''Our refund policy:

**Eligibility:**
- Items must be returned within 30 days
- Products must be unused and in original packaging
- Proof of purchase required

**Process:**
1. Initiate return from "My Orders"
2. Ship the item back to us
3. Once received, we'll process your refund
4. Refund credited within 5-7 business days

**Non-refundable:**
- Opened software or digital products
- Custom/personalized items
- Sale items (unless defective)''',
                'category': payment_cat,
                'order': 3,
            },
            {
                'question': 'How long does a refund take?',
                'answer': '''Refund timeline:

1. **Return Processing:** 3-5 business days after we receive the item
2. **Refund Initiation:** Immediately after approval
3. **Bank Processing:** 5-7 business days

**Total Time:** Approximately 10-14 business days from when we receive your return.

You'll receive email notifications at each step.''',
                'category': payment_cat,
                'order': 4,
            },

            # Products & Catalog category
            {
                'question': 'How do I search for products?',
                'answer': '''You can find products in several ways:

1. **Search Bar:** Enter keywords in the top search bar
2. **Categories:** Browse by product category
3. **Filters:** Use filters to narrow results (price, brand, rating)
4. **Search Autocomplete:** Get suggestions as you type

The search function looks for matches in:
- Product names
- Descriptions
- Categories
- Tags''',
                'category': products_cat,
                'order': 1,
            },
            {
                'question': 'Are product reviews verified?',
                'answer': '''Yes! All product reviews on ShopEase are from verified purchasers.

**Our Review System:**
- Only customers who purchased the product can review it
- Reviews are moderated for spam and inappropriate content
- "Verified Purchase" badge appears on all genuine reviews
- You can rate products 1-5 stars and leave detailed feedback

This ensures authentic, trustworthy product reviews.''',
                'category': products_cat,
                'order': 2,
            },
            {
                'question': 'How do I add items to my cart?',
                'answer': '''To add items to your shopping cart:

1. Browse or search for products
2. Click on a product to view details
3. Select size/color/quantity (if applicable)
4. Click "Add to Cart"
5. Continue shopping or proceed to checkout

**Cart Features:**
- Save items for later
- Update quantities
- Remove items
- View estimated total

Your cart is saved even if you log out!''',
                'category': products_cat,
                'order': 3,
            },
            {
                'question': 'Do you restock out-of-stock items?',
                'answer': '''Most out-of-stock items are restocked regularly.

**To get notified:**
1. Go to the product page
2. Click "Notify Me When Available"
3. Enter your email address
4. You'll receive an alert when it's back in stock

Restock times vary by product. Contact customer support for specific product availability information.''',
                'category': products_cat,
                'order': 4,
            },
        ]

        # Create FAQs
        created_count = 0
        updated_count = 0

        for faq_data in faqs_data:
            faq, created = FAQ.objects.update_or_create(
                question=faq_data['question'],
                defaults=faq_data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  Created: {faq.question[:50]}...'))
            else:
                updated_count += 1
                self.stdout.write(f'  Updated: {faq.question[:50]}...')

        # Summary
        self.stdout.write(self.style.MIGRATE_HEADING('\n=== Seeding Complete ==='))
        self.stdout.write(f'Categories created: 5')
        self.stdout.write(f'FAQs created: {created_count}')
        self.stdout.write(f'FAQs updated: {updated_count}')
        self.stdout.write(f'Total FAQs: {created_count + updated_count}')
        self.stdout.write(self.style.SUCCESS('\n✓ FAQ seeding completed successfully!'))
