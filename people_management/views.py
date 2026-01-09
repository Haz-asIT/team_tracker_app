from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PersonForm, ContractForm
from .models import Person, Contract
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django_filters.views import FilterView
from people_management.filters import ContractFilter
from people_management.models import Person, Contract
from django.core.exceptions import PermissionDenied
from people_management.utils import get_person


# Person Views
class ListPeople(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Person
    context_object_name = "people"
    permission_required = "people_management.view_person"

    def dispatch(self, request, *args, **kwargs):
        person = get_person(request.user)

        # System admin
        if request.user.is_staff or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        # HR admin + Manager allowed
        if person and person.role in ["hr_admin", "manager"]:
            return super().dispatch(request, *args, **kwargs)

        # Employee blocked
        raise PermissionDenied("You are not allowed to view employee list.")

class ViewPersonDetails(LoginRequiredMixin, DetailView):
    model = Person
    template_name = "people_management/person_detail.html"
    context_object_name = "person"

    def dispatch(self, request, *args, **kwargs):
        viewer = get_person(request.user)
        target = self.get_object()

        # System admin can view all
        if request.user.is_staff or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        if not viewer:
            raise PermissionDenied("No person profile linked.")

        # HR admin can view all
        if viewer.role == "hr_admin":
            return super().dispatch(request, *args, **kwargs)

        # Manager can view team under him
        if viewer.role == "manager" and target.manager_id == viewer.id:
            return super().dispatch(request, *args, **kwargs)

        # Employee can view only own profile (optional)
        if target.id == viewer.id:
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied("You are not allowed to view this person.")
class ViewOwnPerson(LoginRequiredMixin, DetailView):
    template_name = "people_management/view_own_person.html"
    context_object_name = "person"

    def get_object(self):
        return get_object_or_404(Person, user=self.request.user)

@login_required
def edit_own_person(request):
    person = request.user.person  # Get the Person object associated with the user
   
    if request.method == "POST":
        form = PersonForm(request.POST, instance=person, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('people_management:view_own_person')  # Redirect to profile page after saving
    else:
        form = PersonForm(instance=person, user=request.user)

    return render(request, 'people_management/edit_own_person.html', {'form': form})
    
# Create and Update Views for Person
class CreateNewPerson(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Person
    form_class = PersonForm
    permission_required = "people_management.add_person"
    success_url = reverse_lazy("people_management:people")

    def form_valid(self, form):
        messages.success(self.request, "Person created successfully!")
        return super().form_valid(form)

class UpdatePerson(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Person
    form_class = PersonForm
    permission_required = "people_management.change_person"
    success_url = reverse_lazy("people_management:people")
    raise_exception = True

    def form_valid(self, form):
        messages.success(self.request, "Person Updated Successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid submission error!")
        return super().form_invalid(form)

class DeletePerson(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Person
    permission_required = "people_management.delete_person"
    success_url = reverse_lazy("people_management:people")

    def form_valid(self, form):
        messages.success(self.request, "Person successfully Deleted!")
        return super().form_valid(form)

# Contract Views
class FilteredContractListView(LoginRequiredMixin, PermissionRequiredMixin, FilterView):
    model = Contract
    filterset_class = ContractFilter
    permission_required = "people_management.view_contract"
    raise_exception = True
    template_name = "people_management/contract_list.html"
    context_object_name = "contracts"

    def dispatch(self, request, *args, **kwargs):
        person = get_person(request.user)

        # System Admin
        if request.user.is_staff or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        # Must have person profile
        if not person:
            raise PermissionDenied("No profile.")

        # HR Admin + Manager can view contract list
        if person.role in ["hr_admin", "manager"]:
            return super().dispatch(request, *args, **kwargs)

        # Employee blocked
        raise PermissionDenied("You are not allowed to view contracts.")

    def get_queryset(self):
        qs = super().get_queryset()
        person = get_person(self.request.user)

        # System Admin / HR Admin see all
        if self.request.user.is_staff or self.request.user.is_superuser:
            return qs
        if person and person.role == "hr_admin":
            return qs

        # Manager sees only contracts of people they manage
        if person and person.role == "manager":
            return qs.filter(person__manager=person)

        return qs.none()


class ViewContractDetails(LoginRequiredMixin, DetailView):
    model = Contract
    template_name = "people_management/contract_detail.html"
    context_object_name = "contract"

    def dispatch(self, request, *args, **kwargs):
        person = get_person(request.user)
        contract = self.get_object()

        # system admin
        if request.user.is_staff or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        if not person:
            raise PermissionDenied("No person profile linked.")

        # HR admin can view all
        if person.role == "hr_admin":
            return super().dispatch(request, *args, **kwargs)

        # manager can view only contracts under his team
        if person.role == "manager" and contract.person.manager_id == person.id:
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied("You are not allowed to view this contract.")
        
class CreateNewContract(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Contract
    form_class = ContractForm
    permission_required = "people_management.add_contract"
    raise_exception = True
    success_url = reverse_lazy("people_management:contracts")

    def dispatch(self, request, *args, **kwargs):
        person = get_person(request.user)

        if request.user.is_staff or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        if person and person.role == "hr_admin":
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied("You are not allowed to create contracts.")

class UpdateContract(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Contract
    form_class = ContractForm
    permission_required = "people_management.change_contract"
    raise_exception = True
    success_url = reverse_lazy("people_management:contracts")

    def dispatch(self, request, *args, **kwargs):
        person = get_person(request.user)

        if request.user.is_staff or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        if person and person.role == "hr_admin":
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied("You are not allowed to update contracts.")

class DeleteContract(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Contract
    permission_required = "people_management.delete_contract"
    raise_exception = True
    success_url = reverse_lazy("people_management:contracts")

    def dispatch(self, request, *args, **kwargs):
        person = get_person(request.user)

        if request.user.is_staff or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        if person and person.role == "hr_admin":
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied("You are not allowed to delete contracts.")