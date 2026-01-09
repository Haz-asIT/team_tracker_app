from django.contrib import admin
from task_management.models import Task  # Only register task model here

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'assigned_to', 'created_at', 'due_date')
    search_fields = ('title', 'description')
    list_filter = ('status', 'priority')

admin.site.register(Task, TaskAdmin)
