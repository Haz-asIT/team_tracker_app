from django.conf import settings
from django.db import models

class SecurityLog(models.Model):
    EVENT_CHOICES = [
        ("LOGIN_SUCCESS", "Login Success"),
        ("LOGIN_FAILED", "Login Failed"),
        ("LOGOUT", "Logout"),
        ("LOCKOUT", "Account Lockout"),
        ("PERMISSION_DENIED", "Permission Denied"),
        ("SUSPICIOUS", "Suspicious Activity"),

        #admin actions
        ("ADMIN_CREATE_USER", "Admin Create User"),
        ("ADMIN_UPDATE_USER", "Admin Update User"),
        ("ADMIN_DELETE_USER", "Admin Delete User"),
        ("ADMIN_CREATE_GROUP", "Admin Create Group"),
        ("ADMIN_UPDATE_GROUP", "Admin Update Group"),
        ("ADMIN_DELETE_GROUP", "Admin Delete Group"),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    event = models.CharField(max_length=64, choices=EVENT_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    target = models.CharField(max_length=200, blank=True)   # e.g., "User: johndoe", "Contract: 12"
    meta = models.JSONField(default=dict, blank=True)       # extra info (NO secrets)
    register(Group)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.created_at} {self.event} {self.actor or 'Anonymous'}"
