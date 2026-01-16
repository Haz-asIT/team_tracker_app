from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group
from itertools import chain

# Import your models
from .models import SecurityLog
from task_management.models import Task
from people_management.models import Person, Contract

class AuditLogListView(LoginRequiredMixin, ListView):
    template_name = "security/audit_log.html"
    context_object_name = "audit_entries"
    permission_required = "security.view_auditlog"

    def dispatch(self, request, *args, **kwargs):
        """
        RBAC Logic:
        1. Allow Superuser (System Admin)
        2. Allow HR Admin
        3. Block everyone else
        """
        is_superuser = request.user.is_superuser
        # Safety check: ensure 'person' exists before checking role
        is_hr_admin = hasattr(request.user, "person") and request.user.person.role == "HR Admin"

        if not (is_superuser or is_hr_admin):
            # Optional: Log the failed attempt
            # log_security_event(request, "PERMISSION_DENIED", ...)
            raise PermissionDenied
            
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        HR ADMIN VIEW:
        Fetches history from Person, Contract, Task, and Group models.
        """
        # 1. Check if user is HR Admin
        if hasattr(self.request.user, "person") and self.request.user.person.role == "HR Admin":
            
            # Fetch history from all tracked models
            person_history = Person.history.all()
            contract_history = Contract.history.all()
            task_history = Task.history.all()
            
            # Handle Group history safely (in case it's not registered)
            try:
                group_history = Group.history.all()
            except AttributeError:
                group_history = []

            # Add a 'model_name' tag so we can show it in the HTML table
            for entry in person_history: entry.model_name = "Person"
            for entry in contract_history: entry.model_name = "Contract"
            for entry in task_history:     entry.model_name = "Task"
            for entry in group_history:    entry.model_name = "Group"

            # Combine all lists and sort by date (newest first)
            combined_history = sorted(
                chain(person_history, contract_history, task_history, group_history),
                key=lambda entry: entry.history_date,
                reverse=True,
            )
            return combined_history[:100] # Limit to latest 100 entries

        # 2. If Superuser, return empty list (they don't see data changes)
        return []

    def get_context_data(self, **kwargs):
        """
        SUPERUSER VIEW:
        Fetches Security Logs (Login/Logout events).
        """
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_superuser:
            # System Admins see Security Logs
            context["security_logs"] = SecurityLog.objects.all().order_by('-created_at')[:100]
        else:
            # HR Admins do not see Security Logs
            context["security_logs"] = None
            
        return context