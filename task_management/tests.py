"""
Task Management Tests.

This module contains tests for the task management CRUD operations,
validating security measures and data validation.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import timedelta

from .models import Task
from .forms import TaskForm
from people_management.models import Person


class TaskModelTest(TestCase):
    """Test cases for the Task model."""

    def setUp(self):
        """Set up test data."""
        self.person = Person.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            date_of_birth="1990-01-01",
            active=True,
        )

    def test_task_creation(self):
        """Test that a task can be created with valid data."""
        task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            status="pending",
            priority="medium",
            created_by=self.person,
        )
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.status, "pending")

    def test_task_str_representation(self):
        """Test the string representation of a task."""
        task = Task.objects.create(
            title="Test Task",
            status="pending",
            created_by=self.person,
        )
        self.assertIn("Test Task", str(task))

    def test_task_is_overdue(self):
        """Test the is_overdue property."""
        # Create an overdue task (skip validation for testing past dates)
        overdue_task = Task(
            title="Overdue Task",
            status="pending",
            due_date=timezone.now().date() - timedelta(days=1),
            created_by=self.person,
        )
        overdue_task._skip_validation = True
        overdue_task.save()
        self.assertTrue(overdue_task.is_overdue)

        # Create a future task
        future_task = Task.objects.create(
            title="Future Task",
            status="pending",
            due_date=timezone.now().date() + timedelta(days=7),
            created_by=self.person,
        )
        self.assertFalse(future_task.is_overdue)

    def test_completed_task_not_overdue(self):
        """Test that completed tasks are not marked as overdue."""
        # Skip validation for testing past dates
        task = Task(
            title="Completed Task",
            status="completed",
            due_date=timezone.now().date() - timedelta(days=1),
            created_by=self.person,
        )
        task._skip_validation = True
        task.save()
        self.assertFalse(task.is_overdue)


class TaskFormTest(TestCase):
    """Test cases for the TaskForm validation."""

    def setUp(self):
        """Set up test data."""
        self.person = Person.objects.create(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            date_of_birth="1985-05-15",
            active=True,
        )

    def test_valid_form(self):
        """Test form with valid data."""
        form_data = {
            "title": "Valid Task Title",
            "description": "A valid description",
            "status": "pending",
            "priority": "medium",
            "due_date": (timezone.now().date() + timedelta(days=7)).isoformat(),
        }
        form = TaskForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_title_too_short(self):
        """Test that titles less than 3 characters are rejected."""
        form_data = {
            "title": "AB",
            "status": "pending",
            "priority": "medium",
        }
        form = TaskForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_title_xss_prevention(self):
        """Test that HTML tags in title are rejected."""
        form_data = {
            "title": "<script>alert('xss')</script>",
            "status": "pending",
            "priority": "medium",
        }
        form = TaskForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_past_due_date_for_new_task(self):
        """Test that past due dates are rejected for new tasks."""
        form_data = {
            "title": "Task with past due date",
            "status": "pending",
            "priority": "medium",
            "due_date": (timezone.now().date() - timedelta(days=1)).isoformat(),
        }
        form = TaskForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("due_date", form.errors)

    def test_invalid_status(self):
        """Test that invalid status values are rejected."""
        form_data = {
            "title": "Task with invalid status",
            "status": "invalid_status",
            "priority": "medium",
        }
        form = TaskForm(data=form_data)
        self.assertFalse(form.is_valid())


class TaskViewTest(TestCase):
    """Test cases for task views."""

    def setUp(self):
        """Set up test data and client."""
        self.client = Client()

        # Create a user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )

        # Create a person linked to the user
        self.person = Person.objects.create(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            date_of_birth="1990-01-01",
            active=True,
            user=self.user,
        )

        # Add permissions
        content_type = ContentType.objects.get_for_model(Task)
        permissions = Permission.objects.filter(content_type=content_type)
        self.user.user_permissions.add(*permissions)

        # Create a test task
        self.task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            status="pending",
            priority="medium",
            created_by=self.person,
        )

    def test_task_list_requires_login(self):
        """Test that task list requires authentication."""
        response = self.client.get(reverse("task_management:task_list"))
        self.assertNotEqual(response.status_code, 200)

    def test_task_list_authenticated(self):
        """Test that authenticated users can view task list."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("task_management:task_list"))
        self.assertEqual(response.status_code, 200)

    def test_task_create_requires_permission(self):
        """Test that task creation requires proper permissions."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("task_management:task_create"))
        self.assertEqual(response.status_code, 200)

    def test_csrf_protection(self):
        """Test that CSRF protection is enforced."""
        from django.test import Client
        # Create a client that enforces CSRF checks
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.login(username="testuser", password="testpass123")
        # POST without CSRF token should fail (403 Forbidden)
        response = csrf_client.post(
            reverse("task_management:task_create"),
            data={"title": "Test Task", "status": "pending", "priority": "medium"},
        )
        # Should be forbidden due to missing CSRF token
        self.assertEqual(response.status_code, 403)


class TaskSecurityTest(TestCase):
    """Test security measures for task management."""

    def test_sql_injection_prevention_in_title(self):
        """Test that SQL injection patterns are rejected."""
        form_data = {
            "title": "'; DROP TABLE tasks; --",
            "status": "pending",
            "priority": "medium",
        }
        form = TaskForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_script_injection_prevention(self):
        """Test that script injection in description is detected."""
        form_data = {
            "title": "Valid Title",
            "description": "<script>document.cookie</script>",
            "status": "pending",
            "priority": "medium",
        }
        form = TaskForm(data=form_data)
        self.assertFalse(form.is_valid())
