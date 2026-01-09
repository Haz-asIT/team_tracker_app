from django.core.exceptions import PermissionDenied

class AuditLogListView(LoginRequiredMixin, ListView):
    template_name = "security/audit_log.html"
    context_object_name = "audit_entries"

    def dispatch(self, request, *args, **kwargs):
        #Ensure that only admin users can access the audit log
        if not hasattr(request.user, "person") or request.user.person.role != "hr_admin":
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #Fetch the latest 100 security log entries
        context["security_logs"] = SecurityLog.objects.all()[:100] 
        return context
