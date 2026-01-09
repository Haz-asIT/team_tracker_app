# Generated migration for task_management

from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("people_management", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text="The title of the task (3-200 characters).",
                        max_length=200,
                        validators=[
                            django.core.validators.MinLengthValidator(
                                3, message="Title must be at least 3 characters long."
                            ),
                            django.core.validators.MaxLengthValidator(
                                200, message="Title cannot exceed 200 characters."
                            ),
                        ],
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Detailed description of the task.",
                        max_length=2000,
                        validators=[
                            django.core.validators.MaxLengthValidator(
                                2000, message="Description cannot exceed 2000 characters."
                            ),
                        ],
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("in_progress", "In Progress"),
                            ("completed", "Completed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        help_text="Current status of the task.",
                        max_length=20,
                    ),
                ),
                (
                    "priority",
                    models.CharField(
                        choices=[
                            ("low", "Low"),
                            ("medium", "Medium"),
                            ("high", "High"),
                            ("urgent", "Urgent"),
                        ],
                        default="medium",
                        help_text="Priority level of the task.",
                        max_length=10,
                    ),
                ),
                (
                    "due_date",
                    models.DateField(
                        blank=True,
                        help_text="The due date for task completion.",
                        null=True,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="Timestamp when the task was created.",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Timestamp when the task was last updated.",
                    ),
                ),
                (
                    "assigned_to",
                    models.ForeignKey(
                        blank=True,
                        help_text="The person assigned to this task.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="assigned_tasks",
                        to="people_management.person",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        help_text="The person who created this task.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_tasks",
                        to="people_management.person",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "permissions": [
                    ("can_assign_task", "Can assign tasks to others"),
                    ("can_change_priority", "Can change task priority"),
                ],
            },
        ),
        migrations.CreateModel(
            name="HistoricalTask",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text="The title of the task (3-200 characters).",
                        max_length=200,
                        validators=[
                            django.core.validators.MinLengthValidator(
                                3, message="Title must be at least 3 characters long."
                            ),
                            django.core.validators.MaxLengthValidator(
                                200, message="Title cannot exceed 200 characters."
                            ),
                        ],
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Detailed description of the task.",
                        max_length=2000,
                        validators=[
                            django.core.validators.MaxLengthValidator(
                                2000, message="Description cannot exceed 2000 characters."
                            ),
                        ],
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("in_progress", "In Progress"),
                            ("completed", "Completed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        help_text="Current status of the task.",
                        max_length=20,
                    ),
                ),
                (
                    "priority",
                    models.CharField(
                        choices=[
                            ("low", "Low"),
                            ("medium", "Medium"),
                            ("high", "High"),
                            ("urgent", "Urgent"),
                        ],
                        default="medium",
                        help_text="Priority level of the task.",
                        max_length=10,
                    ),
                ),
                (
                    "due_date",
                    models.DateField(
                        blank=True,
                        help_text="The due date for task completion.",
                        null=True,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        blank=True,
                        editable=False,
                        help_text="Timestamp when the task was created.",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        blank=True,
                        editable=False,
                        help_text="Timestamp when the task was last updated.",
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "assigned_to",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="people_management.person",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="people_management.person",
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="auth.user",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical task",
                "verbose_name_plural": "historical tasks",
                "db_table": "task_history",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
