"""
Task Management Models.

This module defines the Task model for managing tasks within the team tracker system.
Tasks can be assigned to people and tracked with priorities, statuses, and due dates.
"""

from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from simple_history.models import HistoricalRecords
from people_management.models import Person


class Task(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]

    title = models.CharField(
        max_length=200,
        validators=[
            MinLengthValidator(3, message="Title must be at least 3 characters long."),
            MaxLengthValidator(200, message="Title cannot exceed 200 characters."),
        ],
        help_text="The title of the task (3-200 characters).",
    )

    description = models.TextField(
        max_length=2000,
        blank=True,
        validators=[
            MaxLengthValidator(2000, message="Description cannot exceed 2000 characters."),
        ],
        help_text="Detailed description of the task.",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        help_text="Current status of the task.",
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="medium",
        help_text="Priority level of the task.",
    )

    assigned_to = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
        help_text="The person assigned to this task.",
    )

    created_by = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_tasks",
        help_text="The person who created this task.",
    )

    due_date = models.DateField(
        null=True,
        blank=True,
        help_text="The due date for task completion.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the task was created.",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the task was last updated.",
    )

    # Track historical changes for audit purposes
    history = HistoricalRecords(table_name="task_history")

    class Meta:
        ordering = ["-created_at"]
        permissions = [
            ("can_assign_task", "Can assign tasks to others"),
            ("can_change_priority", "Can change task priority"),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

def clean(self):
    """
    Validate model data before saving.
    """
    super().clean()  # Call parent clean method

    # Validate due_date is not in the past for new tasks
    if self.due_date and not self.pk:
        if self.due_date < timezone.now().date():
            raise ValidationError({
                "due_date": "Due date cannot be in the past for new tasks."
            })

    # Validate title doesn't contain potentially harmful content
    if self.title:
        # Basic XSS prevention - strip HTML tags
        import re
        if re.search(r'<[^>]+>', self.title):
            raise ValidationError({
                "title": "HTML tags are not allowed in the title."
            })

    def save(self, *args, **kwargs):
        """
        Override save to run full validation.
        Skip validation if _skip_validation is set (for testing).
        """
        if not getattr(self, '_skip_validation', False):
            self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        """Check if the task is overdue."""
        if self.due_date and self.status not in ["completed", "cancelled"]:
            return self.due_date < timezone.now().date()
        return False

    @property
    def days_until_due(self):
        """Calculate days until due date."""
        if self.due_date:
            delta = self.due_date - timezone.now().date()
            return delta.days
        return None
