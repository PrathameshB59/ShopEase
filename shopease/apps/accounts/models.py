"""
========================================
USER ACCOUNTS MODELS
========================================

ARCHITECTURE: Extending Django's User Model
--------------------------------------------
Django provides a built-in User model with:
- username, email, password, first_name, last_name
- is_active, is_staff, is_superuser
- date_joined, last_login

We extend it with a Profile model (One-to-One relationship):
- User model: Authentication data (username, password)
- Profile model: Additional data (phone, address, avatar)

Why separate models?
1. Keeps auth data separate from business data
2. Allows custom fields without modifying User table
3. Easier to add features (loyalty points, preferences)

Alternative approach: Custom User Model (more complex)
https://docs.djangoproject.com/en/5.0/topics/auth/customizing/
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """
    User profile extending Django's User model.
    
    Stores additional user information:
    - Contact details (phone)
    - Shipping address
    - Billing address
    - Profile picture
    - Account preferences
    
    Relationship: One-to-One with User
    - Each User has exactly one Profile
    - Each Profile belongs to exactly one User
    
    Real-world example: Amazon user accounts
    - User model: Login credentials
    - Profile: Addresses, phone, payment methods
    """
    
    # One-to-One relationship with User
    # on_delete=CASCADE: Delete profile if user deleted
    # related_name='profile': Access via user.profile
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    # Contact Information
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Phone number with country code"
    )

    # Phone verification (NEW)
    phone_verified = models.BooleanField(
        default=False,
        help_text="Whether phone number is verified"
    )

    otp_code = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        help_text="Current OTP code for verification"
    )

    otp_created_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When OTP was generated"
    )
    
    # Shipping Address
    shipping_address_line1 = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Street address, P.O. box"
    )
    
    shipping_address_line2 = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Apartment, suite, unit, building, floor"
    )
    
    shipping_city = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    
    shipping_state = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    
    shipping_postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    
    shipping_country = models.CharField(
        max_length=100,
        default='India',
        blank=True
    )
    
    # Billing Address (same structure)
    billing_same_as_shipping = models.BooleanField(
        default=True,
        help_text="Use shipping address for billing"
    )
    
    billing_address_line1 = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )
    
    billing_address_line2 = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )
    
    billing_city = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    
    billing_state = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    
    billing_postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    
    billing_country = models.CharField(
        max_length=100,
        default='India',
        blank=True
    )
    
    # Profile Picture
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text="User profile picture"
    )
    
    # Account Preferences
    newsletter_subscribed = models.BooleanField(
        default=False,
        help_text="Receive promotional emails"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        indexes = [
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    # ==========================================
    # HELPER METHODS
    # ==========================================
    
    def get_full_name(self):
        """
        Get user's full name.
        
        Returns: String (First Last or username)
        """
        if self.user.first_name or self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}".strip()
        return self.user.username
    
    def get_shipping_address(self):
        """
        Get formatted shipping address.
        
        Returns: String (multi-line address)
        """
        parts = [
            self.shipping_address_line1,
            self.shipping_address_line2,
            f"{self.shipping_city}, {self.shipping_state} {self.shipping_postal_code}",
            self.shipping_country
        ]
        return "\n".join([p for p in parts if p])
    
    def get_billing_address(self):
        """Get formatted billing address."""
        if self.billing_same_as_shipping:
            return self.get_shipping_address()
        
        parts = [
            self.billing_address_line1,
            self.billing_address_line2,
            f"{self.billing_city}, {self.billing_state} {self.billing_postal_code}",
            self.billing_country
        ]
        return "\n".join([p for p in parts if p])
    
    def has_complete_shipping_address(self):
        """Check if shipping address is complete."""
        return all([
            self.shipping_address_line1,
            self.shipping_city,
            self.shipping_state,
            self.shipping_postal_code,
            self.shipping_country
        ])

    def generate_otp(self):
        """
        Generate 6-digit OTP code.

        Returns: String (6-digit code)
        Security: Random, unpredictable
        """
        import random
        from django.utils import timezone

        # Generate random 6-digit code
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])

        # Save to profile
        self.otp_code = code
        self.otp_created_at = timezone.now()
        self.save()

        return code

    def verify_otp(self, code):
        """
        Verify OTP code.

        Args:
            code: String (user-entered code)

        Returns: Boolean (valid or not)

        Security:
        - Time limit: 10 minutes
        - Single-use: Clears after verification
        - Case-insensitive comparison
        """
        from django.utils import timezone
        from datetime import timedelta

        # Check if OTP exists
        if not self.otp_code:
            return False

        # Check if OTP expired (10 minutes)
        if self.otp_created_at:
            expiry = self.otp_created_at + timedelta(minutes=10)
            if timezone.now() > expiry:
                # OTP expired
                self.otp_code = None
                self.otp_created_at = None
                self.save()
                return False

        # Verify code
        if self.otp_code == code:
            # Mark phone as verified
            self.phone_verified = True
            # Clear OTP (single-use)
            self.otp_code = None
            self.otp_created_at = None
            self.save()
            return True

        return False

    def send_otp_sms(self):
        """
        Send OTP via SMS using Twilio.

        Development mode: Prints to console
        Production mode: Sends real SMS via Twilio

        Returns: OTP code
        """
        from django.conf import settings

        # Generate OTP
        code = self.generate_otp()

        # Check if Twilio is configured
        if settings.TWILIO_ENABLED:
            # PRODUCTION: Send real SMS via Twilio
            try:
                from twilio.rest import Client

                # Initialize Twilio client
                client = Client(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )

                # Send SMS
                message = client.messages.create(
                    body=f"Your ShopEase verification code is: {code}\nValid for 10 minutes.\n\nDo not share this code with anyone.",
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=self.phone
                )

                print(f"SUCCESS - SMS sent to {self.phone} (SID: {message.sid})")

            except Exception as e:
                # Log error but don't crash
                print(f"ERROR - SMS sending failed: {str(e)}")
                # Still return code so development can continue

        else:
            # DEVELOPMENT: Print to console
            import sys
            print(f"\n{'='*60}", flush=True)
            print(f"*** OTP CODE: {code} ***", flush=True)
            print(f"Phone: {self.phone}", flush=True)
            print(f"Valid for 10 minutes", flush=True)
            print(f"Do not share this code", flush=True)
            print(f"{'='*60}\n", flush=True)
            sys.stdout.flush()

        return code

# ==========================================
# SIGNALS - Auto-create Profile
# ==========================================

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create Profile when User is created.
    
    How it works:
    1. User registers → User object created
    2. Signal fires: post_save(User)
    3. This function creates Profile
    
    Why signals?
    - Keeps code DRY (don't repeat in every view)
    - Guarantees Profile exists for every User
    - Django convention (widely used pattern)
    
    Security:
    - No user input involved (safe)
    - Runs in same transaction (atomic)
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save Profile whenever User is saved.

    Ensures Profile stays in sync with User.
    """
    instance.profile.save()


# ==========================================
# USER SESSION TRACKING MODEL
# ==========================================

class UserSession(models.Model):
    """
    Track user login sessions for multi-device support.
    Allows users to see all active sessions and terminate specific ones.

    This enables:
    - Viewing all devices/browsers where user is logged in
    - Remote session termination for security
    - Activity monitoring (last active time)
    - Device/browser identification
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)  # Browser/device info
    device_name = models.CharField(max_length=200, blank=True)  # Parsed from user agent
    location = models.CharField(max_length=200, blank=True)  # Optional: City, Country
    login_time = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-last_activity']
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'

    def __str__(self):
        return f"{self.user.username} - {self.device_name or 'Unknown Device'} ({self.login_time.strftime('%Y-%m-%d %H:%M')})"

    def terminate(self):
        """Terminate this session by deleting the Django session."""
        from django.contrib.sessions.models import Session
        try:
            session = Session.objects.get(session_key=self.session_key)
            session.delete()
        except Session.DoesNotExist:
            pass
        self.is_active = False
        self.save()

    @property
    def is_current(self):
        """Check if this is the current session (for display purposes)."""
        # This will be set in the view when rendering
        return False