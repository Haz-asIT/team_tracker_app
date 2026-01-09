"""
Task Management URL Configuration.

Defines URL patterns for task CRUD operations.
"""
from django.urls import path
from . import views

app_name = "task_management"

urlpatterns = [
    # Task List View for all users (filtered by role)
    path('task-list/', views.TaskListView.as_view(), name='task_list'),

    # Task CRUD Views
    path("create/", views.TaskCreateView.as_view(), name="task_create"),
    path("<int:pk>/", views.TaskDetailView.as_view(), name="task_detail"),
    path("<int:pk>/edit/", views.TaskUpdateView.as_view(), name="task_update"),
    path("<int:pk>/delete/", views.TaskDeleteView.as_view(), name="task_delete"),
]
