from django.core.management.base import BaseCommand
from django.utils import timezone
from documentation.models import DailyIssueHelp


class Command(BaseCommand):
    help = 'Seed help center articles for common daily issues'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING('Seeding Help Center Articles...'))

        help_articles = [
            {
                'title': 'How to Reset Your Password',
                'slug': 'reset-password',
                'issue_type': 'ACCOUNT',
                'problem_description': '''Users often forget their passwords and need a quick way to reset them without contacting support.''',
                'solution_steps': '''Follow these steps to reset your password:

1. Navigate to the login page
2. Click on "Forgot Password?" link below the login form
3. Enter your registered email address
4. Check your email inbox for a password reset link
5. Click the link (valid for 24 hours)
6. Enter your new password (must be at least 8 characters)
7. Confirm your new password
8. Click "Reset Password"

**Important Notes:**
- The reset link expires after 24 hours for security
- Use a strong password with letters, numbers, and special characters
- Don't share your password with anyone

**Still having trouble?**
- Check your spam/junk folder for the reset email
- Make sure you're using the correct email address
- Contact support if you don't receive the email within 5 minutes''',
                'keywords': 'password, reset, forgot, login, access, account recovery',
                'views_count': 150,
                'helpful_count': 120,
            },
            {
                'title': 'Unable to Login - Common Issues',
                'slug': 'login-issues',
                'issue_type': 'ACCOUNT',
                'problem_description': '''Users experiencing difficulties logging into their account.''',
                'solution_steps': '''**Check these common issues:**

1. **Wrong Password**
   - Passwords are case-sensitive
   - Check if Caps Lock is on
   - Try resetting your password

2. **Wrong Email Address**
   - Verify you're using the email you registered with
   - Check for typos in the email

3. **Account Locked (Too Many Failed Attempts)**
   - Wait 30 minutes and try again
   - OR contact support to unlock your account immediately

4. **Browser Issues**
   - Clear your browser cache and cookies
   - Try a different browser
   - Disable browser extensions temporarily

5. **Account Not Verified**
   - Check your email for verification link
   - Resend verification email from login page

**Security Lockout:**
After 5 failed login attempts, your account is temporarily locked for 30 minutes to prevent unauthorized access.''',
                'keywords': 'login, access, locked, wrong password, cannot login, account locked',
                'views_count': 200,
                'helpful_count': 175,
            },
            {
                'title': 'Order Not Showing in My Orders',
                'slug': 'order-not-showing',
                'issue_type': 'ORDER',
                'problem_description': '''Customer placed an order but it doesn\'t appear in their order history.''',
                'solution_steps': '''If your order isn't showing up, check these points:

1. **Wait a Few Minutes**
   - Orders may take 2-3 minutes to appear in your account
   - Refresh your "My Orders" page

2. **Check Confirmation Email**
   - Look for order confirmation in your email
   - Check spam/junk folder
   - The email contains your order number

3. **Logged into Wrong Account**
   - Verify you're using the same email/account you used to place the order
   - If you checked out as guest, you won't see it in account orders

4. **Payment Failed**
   - Check if payment was actually processed
   - Look for payment confirmation from your bank/card
   - If payment failed, the order won't be created

5. **Browser/Session Issues**
   - Try logging out and logging back in
   - Clear cookies and try again

**How to Find Your Order:**
- Use the order number from confirmation email
- Go to "Track Order" and enter order number + email
- Contact support with your order confirmation email''',
                'keywords': 'order, missing, not showing, order history, cannot find order',
                'views_count': 180,
                'helpful_count': 140,
            },
            {
                'title': 'Payment Declined - What to Do',
                'slug': 'payment-declined',
                'issue_type': 'PAYMENT',
                'problem_description': '''Customer\'s payment is being declined during checkout.''',
                'solution_steps': '''**Common Reasons for Payment Decline:**

1. **Insufficient Funds**
   - Check your account balance
   - Ensure you have enough for the order total + any fees

2. **Incorrect Card Details**
   - Verify card number is entered correctly
   - Check expiration date (MM/YY format)
   - Verify CVV (3-4 digit security code)
   - Ensure billing address matches card address

3. **Card Restrictions**
   - Some cards don't support online purchases
   - International cards may be blocked
   - Contact your bank to enable online/international transactions

4. **Bank Security Block**
   - Your bank may be blocking the transaction as suspected fraud
   - Call your bank to authorize the charge
   - Add ShopEase as a trusted merchant

5. **Daily Transaction Limit Exceeded**
   - You may have hit your daily spending limit
   - Wait 24 hours or contact your bank

**Alternative Solutions:**
- Try a different payment method
- Use PayPal or UPI instead of card
- Split payment across multiple cards (if available)
- Contact your bank for authorization''',
                'keywords': 'payment, declined, failed, card rejected, transaction failed, payment error',
                'views_count': 250,
                'helpful_count': 200,
            },
            {
                'title': 'How to Track My Shipment',
                'slug': 'track-shipment',
                'issue_type': 'ORDER',
                'problem_description': '''Customer wants to know where their order is and when it will arrive.''',
                'solution_steps': '''**Tracking Your Order:**

**Method 1: From Your Account**
1. Log into your ShopEase account
2. Go to "My Orders"
3. Click on the order you want to track
4. View real-time tracking information
5. Click "Track Shipment" for detailed courier tracking

**Method 2: Without Login**
1. Go to "Track Order" page
2. Enter your order number (from confirmation email)
3. Enter the email used for the order
4. Click "Track"

**Tracking Status Meanings:**
- **Order Placed:** We've received your order
- **Processing:** Being prepared for shipment
- **Shipped:** Package is with courier
- **Out for Delivery:** Will arrive today
- **Delivered:** Successfully delivered

**Tracking Updates:**
- Updates every 4-6 hours
- Email notifications at each stage
- SMS updates (if opted in)

**No Tracking Info Yet?**
- Allow 24-48 hours after order placement
- Processing time is separate from shipping time
- You'll receive tracking number once shipped''',
                'keywords': 'track, shipment, delivery, where is my order, tracking number, shipping status',
                'views_count': 300,
                'helpful_count': 280,
            },
            {
                'title': 'Item Arrived Damaged - Replacement Process',
                'slug': 'damaged-item',
                'issue_type': 'ORDER',
                'problem_description': '''Product arrived damaged or defective.''',
                'solution_steps': '''**Immediate Steps:**

1. **Take Photos**
   - Photo of outer packaging
   - Photo of damaged item
   - Photo of shipping label
   - Close-up of damage

2. **Don't Throw Away Packaging**
   - Keep all original packaging
   - Keep shipping materials
   - We may need to inspect them

3. **Report Within 48 Hours**
   - Go to your order in "My Orders"
   - Click "Report Issue"
   - Select "Damaged/Defective"
   - Upload photos
   - Describe the damage

**What Happens Next:**

1. **Instant Review:** Our team reviews within 24 hours
2. **Approval:** We approve replacement or refund
3. **Return Pickup:** We arrange free pickup (if needed)
4. **Replacement Shipped:** New item sent immediately
5. **Refund Processed:** OR refund issued to original payment method

**Timeline:**
- Review: 24 hours
- Pickup (if needed): 2-3 business days
- Replacement shipping: 3-5 business days
- Refund: 5-7 business days

**You're Covered:**
- Free return pickup
- Full refund or replacement
- No questions asked
- Fast processing''',
                'keywords': 'damaged, broken, defective, replacement, refund, return, faulty product',
                'views_count': 120,
                'helpful_count': 110,
            },
            {
                'title': 'Shopping Cart Issues - Items Disappearing',
                'slug': 'cart-issues',
                'issue_type': 'TECHNICAL',
                'problem_description': '''Items disappearing from cart or cart not saving properly.''',
                'solution_steps': '''**Common Cart Issues & Solutions:**

1. **Items Disappearing After Logout**
   - **Cause:** Browser cookies disabled
   - **Solution:** Enable cookies in browser settings
   - Items are saved for 30 days when logged in

2. **Cart Empty After Closing Browser**
   - **Cause:** Private/Incognito mode
   - **Solution:** Use normal browsing mode
   - Log into your account to save cart permanently

3. **Can't Add Items to Cart**
   - Check if item is in stock
   - Try different browser
   - Clear browser cache
   - Disable ad blockers temporarily

4. **Quantity Changes Automatically**
   - **Cause:** Stock limitation
   - Maximum available quantity is automatically set
   - Some items have per-order limits

5. **Cart Total Incorrect**
   - Refresh the page
   - Taxes calculated at checkout
   - Shipping costs added at checkout
   - Discounts applied at checkout

**Tips:**
- Save items to Wishlist for later
- Log in to save cart across devices
- Cart items reserved for 30 minutes during checkout
- Items may sell out while in cart (not reserved until checkout)''',
                'keywords': 'cart, shopping cart, items missing, cart empty, cannot add to cart',
                'views_count': 90,
                'helpful_count': 75,
            },
            {
                'title': 'How to Cancel or Modify My Order',
                'slug': 'cancel-modify-order',
                'issue_type': 'ORDER',
                'problem_description': '''Customer wants to cancel or change their order after placing it.''',
                'solution_steps': '''**Cancellation Window:**

**Within 2 Hours of Ordering:**
1. Go to "My Orders"
2. Select the order
3. Click "Cancel Order" button
4. Select cancellation reason
5. Confirm cancellation
6. Refund processed automatically

**After 2 Hours (Before Shipping):**
1. Contact customer support immediately
2. Provide order number
3. We'll try to stop the order from shipping
4. Not guaranteed but we'll do our best

**After Shipping:**
- Can't cancel once shipped
- You can refuse delivery
- Or receive and initiate return
- Full refund in both cases

**Modifying Orders:**

**Change Address (Before Shipping):**
- Contact support with new address
- Possible if order hasn't shipped

**Change Items:**
- Not possible after order placed
- Must cancel and place new order
- OR receive and return unwanted items

**Refund Timeline:**
- Instant cancellation: 5-7 business days
- After shipping: 10-14 business days (includes return time)

**Important:**
- Orders ship fast (usually within 24 hours)
- Act quickly if you need to cancel
- No cancellation fees
- Full refund to original payment method''',
                'keywords': 'cancel, modify, change order, cancel order, edit order, stop order',
                'views_count': 160,
                'helpful_count': 145,
            },
        ]

        created_count = 0
        updated_count = 0

        for article_data in help_articles:
            article, created = DailyIssueHelp.objects.update_or_create(
                slug=article_data['slug'],
                defaults=article_data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  Created: {article.title}'))
            else:
                updated_count += 1
                self.stdout.write(f'  Updated: {article.title}')

        # Summary
        self.stdout.write(self.style.MIGRATE_HEADING('\n=== Seeding Complete ==='))
        self.stdout.write(f'Help articles created: {created_count}')
        self.stdout.write(f'Help articles updated: {updated_count}')
        self.stdout.write(f'Total articles: {created_count + updated_count}')
        self.stdout.write(self.style.SUCCESS('\n✓ Help center seeding completed successfully!'))
