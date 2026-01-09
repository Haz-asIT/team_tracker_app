from django.contrib.auth.signals import user_logged_in, user_login_failed, user_logged_out
from django.dispatch import receiver
from .models import SecurityLog

def get_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    return xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR")

def get_ua(request):
    return request.META.get("HTTP_USER_AGENT", "") if request else ""

@receiver(user_logged_in)
def log_login_success(sender, request, user, **kwargs):
    SecurityLog.objects.create(
        actor=user,
        event="LOGIN_SUCCESS",
        ip_address=get_ip(request),
        user_agent=get_ua(request),
        target=f"user:{user.username}",
        meta={"username": user.username},
    )

@receiver(user_login_failed)
def log_login_failed(sender, credentials, request, **kwargs):
    # IMPORTANT: never log password
    username = credentials.get("username", "")
    SecurityLog.objects.create(
        actor=None,
        event="LOGIN_FAILED",
        ip_address=get_ip(request) if request else None,
        user_agent=get_ua(request),
        target=f"username_attempt:{username}",
        meta={"username": username},
    )

@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    SecurityLog.objects.create(
        actor=user,
        event="LOGOUT",
        ip_address=get_ip(request),
        user_agent=get_ua(request),
        target=f"user:{user.username}",
        meta={"username": user.username},
    )
