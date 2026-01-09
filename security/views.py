from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
    PermissionRequiredMixin,
)
from django.contrib.auth.models import User, Group, Permission
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from django import forms
from .forms import CustomUserCreationForm, CustomLoginForm, CustomUserUpdateForm
from django.contrib.auth.views import LoginView, LogoutView
from people_management.models import Person, Contract
from itertools import chain
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordChangeView,
    PasswordChangeDoneView,
)
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from .models import SecurityLog
from django.core.exceptions import PermissionDenied
from .forms import CustomPasswordChangeForm

# Keep this as TOP-LEVEL function
def log_security_event(request, event, target="", meta=None):
    SecurityLog.objects.create(
        actor=request.user if request.user.is_authenticated else None,
        event=event,
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        target=target,
        meta=meta or {},  # store only IDs or non-sensitive info
    )


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "security/auth/password_reset_complete.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "security/auth/password_reset_confirm.html"


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "security/auth/password_reset_done.html"


class CustomPasswordResetView(PasswordResetView):
    template_name = "security/auth/password_reset.html"

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "security/auth/password_change_form.html"
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy("security:password_change_done")

    def form_valid(self, form):
        messages.success(self.request, "✅ Password updated successfully!")
        return super().form_valid(form)

class CustomPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = "security/auth/password_change_done.html"

class LoginInterface(LoginView):
    form_class = CustomLoginForm
    template_name = "security/auth/login.html"
    redirect_authenticated_user = True
    success_url = reverse_lazy("dashboard:dashboard")

    def form_valid(self, form):
        user = form.get_user()

        # log success
        log_security_event(
            self.request,
            "LOGIN_SUCCESS",
            target=f"user:{user.username}",
            meta={"user_id": user.id},
        )

        messages.info(self.request, "You have logged in successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        # log failed attempt (never store password)
        attempted_username = self.request.POST.get("username", "").strip()

        log_security_event(
            self.request,
            "LOGIN_FAILED",
            target=f"username_attempt:{attempted_username}",
            meta={},  # keep empty or only non-sensitive
        )

        messages.error(self.request, "Login failed. Please check your username/password.")
        return super().form_invalid(form)


@method_decorator(require_POST, name="dispatch")
class LogoutInterface(LogoutView):
    next_page = reverse_lazy("security:login")

    def dispatch(self, request, *args, **kwargs):
        # log logout
        if request.user.is_authenticated:
            log_security_event(
                request,
                "LOGOUT",
                target=f"user:{request.user.username}",
                meta={"user_id": request.user.id},
            )

        messages.info(request, "You have been logged out.")
        return super().dispatch(request, *args, **kwargs)


# ==========================
# User Management Views
# ==========================
class ListUsers(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = User
    context_object_name = "users"
    template_name = "security/users/list.html"
    permission_required = "auth.view_user"


class ViewUserDetails(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = User
    context_object_name = "user"
    template_name = "security/users/detail.html"
    permission_required = "auth.view_user"


class CreateNewUser(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = "security/users/form.html"
    success_url = reverse_lazy("security:user_list")
    permission_required = "auth.add_user"

    def form_valid(self, form):
        # Let CBV handle saving so self.object is set correctly
        response = super().form_valid(form)

        # If still want is_staff=True, set it AFTER save
        self.object.is_staff = True
        self.object.save(update_fields=["is_staff"])

        log_security_event(
            self.request,
            "ADMIN_CREATE_USER",
            target=f"user:{self.object.username}",
            meta={"created_user_id": self.object.id},
        )

        messages.success(self.request, "User successfully created!")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Invalid submission error!")
        return super().form_invalid(form)


class UpdateUser(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserUpdateForm
    template_name = "security/users/form.html"
    success_url = reverse_lazy("security:user_list")
    permission_required = "auth.change_user"

    def form_valid(self, form):
        response = super().form_valid(form)

        log_security_event(
            self.request,
            "ADMIN_UPDATE_USER",
            target=f"user:{self.object.username}",
            meta={"updated_user_id": self.object.id},
        )

        messages.success(self.request, "User successfully updated!")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Invalid submission error!")
        return super().form_invalid(form)


class DeleteUser(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = User
    template_name = "security/users/confirm_delete.html"
    success_url = reverse_lazy("security:user_list")
    permission_required = "auth.delete_user"

    def form_valid(self, form):
        obj = self.get_object()

        log_security_event(
            self.request,
            "ADMIN_DELETE_USER",
            target=f"user:{obj.username}",
            meta={"deleted_user_id": obj.id},
        )

        return super().form_valid(form)

# ==========================
# Group Management
# ==========================
class GroupForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Group
        fields = ["name", "permissions"]


class ListGroups(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Group
    context_object_name = "groups"
    template_name = "security/groups/list.html"
    permission_required = "auth.view_group"


class GroupDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Group
    template_name = "security/groups/detail.html"
    context_object_name = "group"
    permission_required = "auth.view_group"


class CreateGroup(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Group
    form_class = GroupForm
    template_name = "security/groups/form.html"
    success_url = reverse_lazy("security:group_list")
    permission_required = "auth.add_group"

    def form_valid(self, form):
        response = super().form_valid(form)

        log_security_event(
            self.request,
            "ADMIN_CREATE_GROUP",
            target=f"group:{self.object.name}",
            meta={"created_group_id": self.object.id},
        )

        messages.success(self.request, "Group successfully created!")
        return response


class UpdateGroup(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Group
    form_class = GroupForm
    template_name = "security/groups/form.html"
    success_url = reverse_lazy("security:group_list")
    permission_required = "auth.change_group"

    def form_valid(self, form):
        response = super().form_valid(form)

        log_security_event(
            self.request,
            "ADMIN_UPDATE_GROUP",
            target=f"group:{self.object.name}",
            meta={"updated_group_id": self.object.id},
        )

        messages.success(self.request, "Group successfully updated!")
        return response


class DeleteGroup(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Group
    template_name = "security/groups/confirm_delete.html"
    success_url = reverse_lazy("security:group_list")
    permission_required = "auth.delete_group"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()

        log_security_event(
            request,
            "ADMIN_DELETE_GROUP",
            target=f"group:{obj.name}",
            meta={"deleted_group_id": obj.id},
        )

        messages.warning(self.request, "Group deleted.")
        return super().delete(request, *args, **kwargs)


# ==========================
# Audit Log (Admin only)
# ==========================

class AuditLogListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    template_name = "security/audit_log.html"
    context_object_name = "audit_entries"

    permission_required = "security.view_securitylog"
    raise_exception = True  # show 403 instead of redirect

    def handle_no_permission(self):
        # Log forbidden access attempts (no sensitive data)
        log_security_event(
            self.request,
            "PERMISSION_DENIED",
            target=f"path:{self.request.path}",
            meta={
                "required_perm": self.permission_required,
                "view": "AuditLogListView",
            },
        )
        return super().handle_no_permission()

    def get_queryset(self):
        person_history = Person.history.model.objects.all()
        contract_history = Contract.history.all()

        for entry in person_history:
            entry.model_name = entry.instance.__class__.__name__
        for entry in contract_history:
            entry.model_name = entry.instance.__class__.__name__

        combined_history = sorted(
            chain(person_history, contract_history),
            key=lambda entry: entry.history_date,
            reverse=True,
        )
        return combined_history[:100]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["security_logs"] = SecurityLog.objects.all()[:100]
        return context
