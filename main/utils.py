from django.utils import timezone
import pytz
from datetime import timedelta

ASIA_KOLKATA = pytz.timezone('Asia/Kolkata')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_now():
    """Get current time in Asia/Kolkata timezone, always timezone-aware."""
    now = timezone.now()
    if timezone.is_naive(now):
        now = timezone.make_aware(now)
    return now.astimezone(ASIA_KOLKATA)
