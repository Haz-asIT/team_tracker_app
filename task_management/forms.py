"""
Task Management Forms.

This module defines Django forms for managing Task model.
It provides validation logic and custom widgets for secure data input.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.html import escape
import re

from .models import Task
from people_management.models import Person


class TaskForm(forms.ModelForm):
    """
    Form for creating and updating Task instances.
    Implements comprehensive input validation and sanitization.
    """

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "status",
            "priority",
            "assigned_to",
            "due_date",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter task title",
                    "maxlength": "200",
                    "minlength": "3",
                    "required": True,
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter task description",
                    "rows": 4,
                    "maxlength": "2000",
                }
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "assigned_to": forms.Select(attrs={"class": "form-select"}),
            "due_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
        }
        error_messages = {
            "title": {
                "required": "Task title is required.",
                "max_length": "Title cannot be longer than 200 characters.",
                "min_length": "Title must be at least 3 characters long.",
            },
            "description": {
                "max_length": "Description cannot exceed 2000 characters.",
            },
        }

    def __init__(self, *args, **kwargs):
        """
        Initialize the TaskForm.
        Filter assigned_to queryset to only active persons.
        """
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Only show active persons for assignment
        self.fields["assigned_to"].queryset = Person.objects.filter(active=True)
        self.fields["assigned_to"].required = False

        # If editing an existing task, allow keeping current status
        if self.instance.pk:
            self.fields["status"].required = True
        else:
            # For new tasks, default to pending
            self.fields["status"].initial = "pending"

    def clean_title(self):
        """
        Validate and sanitize the title field.
        - Prevents XSS attacks by escaping HTML
        - Prevents SQL injection patterns
        - Ensures minimum length
        """
        title = self.cleaned_data.get("title", "").strip()

        if not title:
            raise ValidationError("Task title cannot be empty.")

        if len(title) < 3:
            raise ValidationError("Title must be at least 3 characters long.")

        if len(title) > 200:
            raise ValidationError("Title cannot exceed 200 characters.")

        # Check for HTML tags (XSS prevention)
        if re.search(r'<[^>]+>', title):
            raise ValidationError("HTML tags are not allowed in the title.")

        # Check for potential SQL injection patterns
        sql_patterns = [
            r"('|\")\s*(OR|AND)\s*('|\"|[0-9])",
            r";\s*(DROP|DELETE|UPDATE|INSERT|SELECT)",
            r"--\s*$",
            r"/\*.*\*/",
        ]
        for pattern in sql_patterns:
            if re.search(pattern, title, re.IGNORECASE):
                raise ValidationError("Invalid characters detected in title.")

        return escape(title)

    def clean_description(self):
        """
        Validate and sanitize the description field.
        - Escapes HTML to prevent XSS
        - Limits length
        """
        description = self.cleaned_data.get("description", "").strip()

        if len(description) > 2000:
            raise ValidationError("Description cannot exceed 2000 characters.")

        # Check for script tags specifically (XSS prevention)
        if re.search(r'<script[^>]*>.*?</script>', description, re.IGNORECASE | re.DOTALL):
            raise ValidationError("Script tags are not allowed.")

        return description

    def clean_due_date(self):
    due_date = self.cleaned_data.get("due_date")

    if due_date and not self.instance.pk:
        if due_date < timezone.localdate():
            raise ValidationError("Due date cannot be in the past for new tasks.")

        return due_date

    def clean_status(self):
        """
        Validate status transitions.
        """
        status = self.cleaned_data.get("status")
        valid_statuses = [choice[0] for choice in Task.STATUS_CHOICES]

        if status not in valid_statuses:
            raise ValidationError("Invalid status selected.")

        return status

    def clean_priority(self):
        """
        Validate priority value.
        """
        priority = self.cleaned_data.get("priority")
        valid_priorities = [choice[0] for choice in Task.PRIORITY_CHOICES]

        if priority not in valid_priorities:
            raise ValidationError("Invalid priority selected.")

        return priority

    def clean(self):
        """
        Perform cross-field validation.
        """
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        assigned_to = cleaned_data.get("assigned_to")

        # If task is in progress, it should be assigned to someone
        if status == "in_progress" and not assigned_to:
            self.add_error(
                "assigned_to",
                "A task in progress should be assigned to someone."
            )

        return cleaned_data


class TaskFilterForm(forms.Form):
    """
    Form for filtering tasks in list view.
    """

    STATUS_CHOICES = [("", "All Statuses")] + list(Task.STATUS_CHOICES)
    PRIORITY_CHOICES = [("", "All Priorities")] + list(Task.PRIORITY_CHOICES)

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    assigned_to = forms.ModelChoiceField(
        queryset=Person.objects.filter(active=True),
        required=False,
        empty_label="All Assignees",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search tasks...",
                "maxlength": "100",
            }
        ),
    )

    def clean_search(self):
        """
        Sanitize search input to prevent injection attacks.
        """
        search = self.cleaned_data.get("search", "").strip()

        if len(search) > 100:
            raise ValidationError("Search query too long.")

        # Remove potentially dangerous characters
        search = re.sub(r'[<>"\';]', '', search)

        return search
