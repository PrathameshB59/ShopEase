"""
========================================
ACCOUNT BACKGROUND TASKS
========================================

Celery tasks for account management:
- Send OTP SMS via Twilio
- Send password reset emails
- Clean expired sessions
"""

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_otp_sms(self, phone_number, otp_code):
    """
    Send OTP via Twilio SMS.

    Args:
        phone_number: User's phone number
        otp_code: 6-digit OTP code
    """
    try:
        # Check if Twilio is enabled
        twilio_enabled = getattr(settings, 'TWILIO_ENABLED', False)

        if not twilio_enabled:
            logger.info(f"Development mode - OTP for {phone_number}: {otp_code}")
            return f"DEVELOPMENT MODE - OTP: {otp_code}"

        from twilio.rest import Client

        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )

        message = client.messages.create(
            body=f'Your ShopEase OTP is: {otp_code}. Valid for 10 minutes.',
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )

        logger.info(f"OTP SMS sent to {phone_number}")
        return f"SMS sent: {message.sid}"

    except Exception as exc:
        logger.error(f"Error sending OTP SMS: {exc}")
        raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))


@shared_task
def send_password_reset_email(user_email, reset_link):
    """
    Send password reset email.

    Args:
        user_email: User's email address
        reset_link: Password reset URL
    """
    try:
        subject = 'Reset Your ShopEase Password'
        message = f'''
        You requested to reset your ShopEase password.

        Click the link below to reset your password:
        {reset_link}

        This link expires in 1 hour.

        If you didn't request this, ignore this email.
        '''

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )

        logger.info(f"Password reset email sent to {user_email}")

    except Exception as exc:
        logger.error(f"Error sending password reset email: {exc}")


@shared_task
def clean_expired_sessions():
    """
    Delete expired sessions from database.

    Runs daily via Celery Beat.
    """
    try:
        expired_count = Session.objects.filter(expire_date__lt=timezone.now()).count()
        Session.objects.filter(expire_date__lt=timezone.now()).delete()
        logger.info(f"Cleaned {expired_count} expired sessions")
        return f"Cleaned {expired_count} sessions"

    except Exception as exc:
        logger.error(f"Error cleaning sessions: {exc}")
