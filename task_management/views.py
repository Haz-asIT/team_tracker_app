from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied

from task_management.models import Task
from people_management.utils import get_person, is_hr_admin, is_manager


# =========================
# 2(A) Task List View (RBAC queryset)
# =========================
class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "task_management/task_list.html"
    context_object_name = "tasks"
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        person = get_person(user)

        # Admin / HR admin: all tasks
        if is_hr_admin(user):
            tasks = Task.objects.all()

        # Manager: tasks assigned to their team
        elif is_manager(user) and person:
            tasks = Task.objects.filter(assigned_to__manager=person)

        # Employee: only own tasks
        elif person:
            tasks = Task.objects.filter(assigned_to=person)

        # No Person linked -> show nothing (prevents crash)
        else:
            tasks = Task.objects.none()

        # Optional filters
        status = self.request.GET.get("status")
        if status:
            tasks = tasks.filter(status=status)

        priority = self.request.GET.get("priority")
        if priority:
            tasks = tasks.filter(priority=priority)

        search = self.request.GET.get("search")
        if search:
            tasks = tasks.filter(title__icontains=search)

        return tasks


# =========================
# Create Task (only admin/manager usually)
# =========================
class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = "task_management/task_form.html"
    fields = ["title", "description", "status", "priority", "assigned_to", "due_date"]
    success_url = reverse_lazy("task_management:task_list")

    def dispatch(self, request, *args, **kwargs):
        # Optional: only admin/manager can create tasks
        if is_hr_admin(request.user) or is_manager(request.user):
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied("You are not allowed to create tasks.")

    def form_valid(self, form):
        person = get_person(self.request.user)
        if not person:
            raise PermissionDenied("User has no Person profile.")
        form.instance.created_by = person
        return super().form_valid(form)


# =========================
# Detail View (everyone can view if they can see in queryset)
# =========================
class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "task_management/task_detail.html"
    context_object_name = "task"

    def dispatch(self, request, *args, **kwargs):
        """
        Ensure employee can only view their own task,
        manager can view team tasks,
        admin can view all.
        """
        user = request.user
        person = get_person(user)
        task = self.get_object()

        if is_hr_admin(user):
            return super().dispatch(request, *args, **kwargs)

        if not person:
            raise PermissionDenied("User has no Person profile.")

        # manager can view team tasks
        if is_manager(user) and task.assigned_to and task.assigned_to.manager_id == person.id:
            return super().dispatch(request, *args, **kwargs)

        # employee can view only own task
        if task.assigned_to_id == person.id:
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied("You are not allowed to view this task.")


# =========================
# 2(B) Update View (block employees)
# =========================
class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    template_name = "task_management/task_form.html"
    fields = ["title", "description", "status", "priority", "assigned_to", "due_date"]
    success_url = reverse_lazy("task_management:task_list")

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        person = get_person(user)
        task = self.get_object()

        if is_hr_admin(user):
            return super().dispatch(request, *args, **kwargs)

        if not person:
            raise PermissionDenied("User has no Person profile.")

        # Manager can edit tasks for their team only
        if is_manager(user) and task.assigned_to and task.assigned_to.manager_id == person.id:
            return super().dispatch(request, *args, **kwargs)

        # Employee cannot edit
        raise PermissionDenied("You are not allowed to edit tasks.")


# =========================
# 2(B) Delete View (block employees)
# =========================
class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = "task_management/task_confirm_delete.html"
    success_url = reverse_lazy("task_management:task_list")

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        person = get_person(user)
        task = self.get_object()

        if is_hr_admin(user):
            return super().dispatch(request, *args, **kwargs)

        if not person:
            raise PermissionDenied("User has no Person profile.")

        # Manager can delete tasks for their team only
        if is_manager(user) and task.assigned_to and task.assigned_to.manager_id == person.id:
            return super().dispatch(request, *args, **kwargs)

        # Employee cannot delete
        raise PermissionDenied("You are not allowed to delete tasks.")
