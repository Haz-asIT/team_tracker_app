from django.contrib import admin
from .models import Person, Contract

class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number')  # Removed status
    search_fields = ('first_name', 'last_name', 'email')
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_staff:
            return queryset  # Admin can see all employees
        elif request.user.person and request.user.person.role == "Manager":
            return queryset.filter(manager=request.user.person)  # Manager sees only their team members
        else:
            return queryset.filter(id=request.user.person.id)  # Employee sees only their own details

    def has_change_permission(self, request, obj=None):
        if request.user.is_staff:
            return True  # Admin can edit any employee
        if obj and obj.id == request.user.person.id:
            return True  # Employee can edit only their own details
        return False

class ContractAdmin(admin.ModelAdmin):
    list_display = ('person', 'job_title', 'hourly_rate', 'contracted_hours', 'contract_start', 'contract_end')
    search_fields = ('person__first_name', 'person__last_name', 'job_title')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_staff:
            return queryset  # Admin can see all contracts
        elif request.user.person and request.user.person.role == "Manager":
            return queryset.filter(person__manager=request.user.person)  # Manager sees only their team members' contracts
        else:
            return queryset.filter(person=request.user.person)  # Employee sees only their own contract

    def has_change_permission(self, request, obj=None):
        if request.user.is_staff:
            return True  # Admin can edit any contract
        if obj and obj.person.id == request.user.person.id:
            return True  # Employee can edit only their own contract
        return False

admin.site.register(Person, PersonAdmin)
admin.site.register(Contract, ContractAdmin)
