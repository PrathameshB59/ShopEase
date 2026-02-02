"""
Session tracking middleware.
Updates UserSession records on each request.
"""
from django.utils.deprecation import MiddlewareMixin
from .models import UserSession
from django.utils import timezone


class SessionTrackingMiddleware(MiddlewareMixin):
    """Track user sessions and update last_activity timestamp."""

    def process_request(self, request):
        if request.user.is_authenticated and request.session.session_key:
            # Update or create session record
            UserSession.objects.update_or_create(
                session_key=request.session.session_key,
                defaults={
                    'user': request.user,
                    'ip_address': self.get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'device_name': self.parse_device_name(request.META.get('HTTP_USER_AGENT', '')),
                    'last_activity': timezone.now(),
                    'is_active': True,
                }
            )

    def get_client_ip(self, request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def parse_device_name(self, user_agent):
        """Parse user agent to extract device/browser name."""
        ua = user_agent.lower()

        # Browser detection
        if 'edg' in ua:
            browser = 'Edge'
        elif 'chrome' in ua:
            browser = 'Chrome'
        elif 'firefox' in ua:
            browser = 'Firefox'
        elif 'safari' in ua and 'chrome' not in ua:
            browser = 'Safari'
        elif 'opera' in ua or 'opr' in ua:
            browser = 'Opera'
        else:
            browser = 'Unknown Browser'

        # OS detection
        if 'windows' in ua:
            os_name = 'Windows'
        elif 'mac' in ua:
            os_name = 'macOS'
        elif 'linux' in ua:
            os_name = 'Linux'
        elif 'android' in ua:
            os_name = 'Android'
        elif 'iphone' in ua or 'ipad' in ua:
            os_name = 'iOS'
        else:
            os_name = 'Unknown OS'

        return f"{browser} on {os_name}"
