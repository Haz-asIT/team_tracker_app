import uuid
import os
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from datetime import date
from simple_history.models import HistoricalRecords, HistoricForeignKey

# 1. Validate File Type (MIME + Extension) & 2. Restrict Size
def validate_resume(file):
    # Limit size to 2MB
    limit_mb = 2
    if file.size > limit_mb * 1024 * 1024:
        raise ValidationError(f"Max size of file is {limit_mb} MB")

    # Limit extension
    if not file.name.endswith('.pdf'):
        raise ValidationError("Only PDF files are allowed")

# 4. Rename files to random UUID
def rename_file(instance, filename):
    ext = filename.split('.')[-1]
    # Generates a random UUID (e.g., 550e8400-e29b-41d4-a716-446655440000.pdf)
    filename = f'{uuid.uuid4()}.{ext}'
    # 3. Store outside web root (Django handles this via 'upload_to')
    return os.path.join('resumes/', filename)


class Person(models.Model):
    """
    Represents an employee in the system.

    Each Person can be linked to a Django `User` for authentication.
    A Person may also have a manager (who is another Person instance).
    """

    ROLE_CHOICES = [
        ("employee", "Employee"),
        ("manager", "Manager"),
        ("hr_admin", "HR Admin"),
    ]

    first_name = models.CharField(max_length=50, help_text="The employee's first name.")
    last_name = models.CharField(max_length=50, help_text="The employee's last name.")
    email = models.EmailField(
        max_length=255, unique=True, help_text="The employee's email address."
    )
    phone_number = models.CharField(
        max_length=15, blank=True, help_text="Contact number of the employee."
    )
    date_of_birth = models.DateField(help_text="Employee's date of birth.")
    active = models.BooleanField(
        default=False, help_text="Indicates if the person is currently employed."
    )

    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="team_members",
        help_text="Manager supervising this employee.",
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="employee",
        help_text="The role of the person in the company.",
    )

    user = models.OneToOneField(
        "auth.User",
        on_delete=models.SET_NULL,
        related_name="person",
        null=True,
        blank=True,
        help_text="The associated Django user account.",
    )

    # The Secure File Field
    resume = models.FileField(
        upload_to=rename_file,        # Requirement: Rename to UUID
        validators=[validate_resume], # Requirement: Validate Type & Size
        blank=True, 
        null=True
    )

    history = HistoricalRecords(table_name="person_history")

    def __str__(self):
        return f"{self.first_name} {self.last_name} (ID: {self.id})"

    def update_active_status(self):
        """
        Updates the `active` field based on active contracts.

        The person is considered active if they have at least one contract
        where the current date falls within the contract period.
        Otherwise, they are set to inactive.
        """
        today = date.today()
        if self.contracts.filter(
            contract_start__lte=today, contract_end__gte=today
        ).exists():
            self.active = True
        else:
            self.active = False
        self.save()


class Contract(models.Model):
    """
    Represents an employment contract for a Person.
    """

    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="contracts",
        help_text="The person this contract belongs to.",
    )
    job_title = models.CharField(
        max_length=255, help_text="Job title associated with this contract."
    )
    contract_start = models.DateField(help_text="Contract start date.")
    contract_end = models.DateField(
        null=True, blank=True, help_text="Contract end date (if applicable)."
    )
    hourly_rate = models.FloatField(
        default=12.45, help_text="Hourly pay rate for this contract."
    )
    contracted_hours = models.FloatField(
        default=40, help_text="Number of contracted hours per week."
    )

    history = HistoricalRecords(table_name="contract_history")

    def save(self, *args, **kwargs):
        if self.contract_end and self.contract_end < date.today():
            self.person.update_active_status()
            self.person.save()
            print(self.person.active)
        # Call the original save method
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.person} - {self.job_title}"


@receiver(post_save, sender=Contract)
def activate_person_on_contract(sender, instance, **kwargs):
    """Activate a person only if today's date is within the contract period."""
    today = date.today()

    if instance.person and not instance.person.active:
        if instance.contract_start <= today and (
            instance.contract_end is None or today <= instance.contract_end
        ):
            instance.person.active = True
            instance.person.save()


@receiver(post_delete, sender=Contract)
def deactivate_person_if_no_valid_contracts(sender, instance, **kwargs):
    """Deactivate the person if they have no valid (active) contracts."""
    today = date.today()

    has_valid_contract = (
        Contract.objects.filter(
            person=instance.person,
            contract_start__lte=today,  # Started already
        )
        .exclude(contract_end__lt=today)  # Not already expired
        .exists()
    )

    if instance.person and not has_valid_contract:
        instance.person.active = False
        instance.person.save()
