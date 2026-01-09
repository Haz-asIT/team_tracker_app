from django.contrib import admin
from .models import SecurityLog

@admin.register(SecurityLog)
class SecurityLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "event", "actor", "ip_address", "target")
    list_filter = ("event", "created_at")
    search_fields = ("target", "user__username", "ip_address")
