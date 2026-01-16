from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import Person, Contract
from django.core.validators import RegexValidator, EmailValidator


# PERSON FORM (Fixed for Edit Profile)
class PersonForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50,
        validators=[RegexValidator(r'^[A-Za-z\s\-]+$', 'Invalid characters')]
    )
    last_name = forms.CharField(
        max_length=50,
        validators=[RegexValidator(r'^[A-Za-z\s\-]+$', 'Last name contains invalid characters.')]
    )
    email = forms.EmailField(validators=[EmailValidator()])
    phone_number = forms.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?[\d\-\s]{7,20}$', 'Enter a valid phone number.')]
    )
    manager = forms.ModelChoiceField(
        # detailed filter to catch strict lowercase OR capitalized versions
        queryset=Person.objects.filter(role__in=[
            'Manager', 'Manager',
            'HR Admin', 'HR Admin'
        ]),
        required=False,
        empty_label="---------",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Person
        fields = ["first_name", "last_name", "email", "phone_number", "date_of_birth", "role", "manager"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "First Name"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Last Name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone Number"}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "role": forms.Select(attrs={"class": "form-select"}),
            "manager": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):

        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.fields["role"].required = True
        self.fields["manager"].queryset = Person.objects.filter(
            role__in=["Manager", "HR Admin"]
        )
        self.fields["manager"].required = False

        # FIX: Lock fields for standard users using Django's .disabled property
        # This tells Django: "Don't validate these fields, just keep the database value."
        if self.user and not self.user.is_superuser:
            self.fields['first_name'].disabled = True
            self.fields['last_name'].disabled = True
            self.fields['role'].disabled = True
            self.fields['manager'].disabled = True

    def clean_email(self):
        email = self.cleaned_data["email"]
        if email and "@" not in email:
            raise ValidationError("No domain for email")
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name", "").strip()
        if not first_name:
            raise ValidationError("First name cannot be empty")
        return first_name

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get("date_of_birth")
        if dob:
            today = date.today()
            age = (
                today.year
                - dob.year
                - ((today.month, today.day) < (dob.month, dob.day))
            )
            if age < 18:
                raise ValidationError("Person must be at least 18 years old")
        return dob

    def clean_manager(self):
        manager = self.cleaned_data.get("Manager")
        if manager and manager.role == "Employee":
            raise ValidationError("An employee cannot be assigned as a manager.")
        return manager

# CONTRACT FORM 

class ContractForm(forms.ModelForm):
    """
    Form for creating and updating Contract instances.
    """
    class Meta:
        model = Contract
        fields = [
            "person",
            "job_title",
            "contract_start",
            "contract_end",
            "hourly_rate",
            "contracted_hours",
        ]
        widgets = {
            "person": forms.Select(attrs={"class": "form-select"}),
            "job_title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Job Title"}
            ),
            "contract_start": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "contract_end": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "hourly_rate": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Hourly Rate"}
            ),
            "contracted_hours": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Contracted Hours"}
            ),
        }
        error_messages = {
            "job_title": {
                "max_length": "Job title cannot be longer than 255 characters!"
            },
        }

    def clean_hourly_rate(self):
        """
        Validate the hourly rate to ensure it meets the minimum threshold.
        """
        hourly_rate = self.cleaned_data.get("hourly_rate")
        if hourly_rate is not None and hourly_rate < 12.45:
            raise ValidationError("Hourly rate cannot be lower than 12.45")
        return hourly_rate

    def clean_contract_end(self):
        """
        Validate the contract end date to ensure it is after the contract start date.
        """
        contract_start = self.cleaned_data.get("contract_start")
        contract_end = self.cleaned_data.get("contract_end")
        if contract_end and contract_start and contract_end <= contract_start:
            raise ValidationError("Contract end date must be after contract start date")
        return contract_end