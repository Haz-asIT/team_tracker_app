from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from people_management.models import Person, Contract
from task_management.models import Task 
from django.db.models import Q

class DashboardView(LoginRequiredMixin, TemplateView):
    """
    View for the main dashboard, displaying relevant data based on user roles.

    - Employees: See only their own details (and no contracts or tasks).
    - Managers: See their assigned team members, contracts for their team, and tasks for their team.
    - HR/Admins: See all employees, all contracts, and all tasks.

    Access Control:
    - Users must be logged in (redirects to login page if not authenticated).
    - Managers can only access their direct team.
    - Employees do not see the people management table or tasks.
    """

    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        """
        Get context data for the dashboard template.

        This method adds the following context variables based on the logged-in user's role:

        - person: The logged-in user's personal details.
        - people: A list of employees visible to the user:
            - HR/Admin: All employees.
            - Manager: Employees in the manager's team.
            - Employee: None (or personal details only).
        - contracts: A list of contracts visible to the user:
            - HR/Admin: All contracts.
            - Manager: Contracts for employees in the manager's team.
            - Employee: None (employees do not see any contracts).
        - tasks: A list of tasks visible to the user:
            - HR/Admin: All tasks.
            - Manager: Tasks assigned to their team members.
            - Employee: Only their own tasks.

        Returns:
            dict: A dictionary with keys 'person', 'people', 'contracts', and 'tasks' for the template.
        """
        print("DASHBOARD VIEW HIT:", self.request.user.is_authenticated)
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Ensure the user is linked to a Person record
        person = getattr(user, "person", None)
        context["person"] = person

        if person:
            # Role-based filtering for people
            if person.role == "HR Admin":
                # HR Admins see all employees
                context["people"] = Person.objects.all()
            elif person.role == "Manager":
                # Managers see only their assigned team members
                context["people"] = Person.objects.filter(manager=person)
            else:
                # Employees only see their own details (no people list)
                context["people"] = None

            # Role-based filtering for contracts
            if person.role == "HR Admin":
                # HR Admins see all contracts
                context["contracts"] = Contract.objects.all()
            elif person.role == "Manager":
                # Managers see contracts for their team members (assuming Contract has a ForeignKey to Person)
                context["contracts"] = Contract.objects.filter(person__manager=person)
            else:
                # Employees do not get any contract context
                context["contracts"] = None

            # Role-based filtering for tasks
            if person.role == "HR Admin":
                # HR Admins see all tasks
                context["tasks"] = Task.objects.all()
            elif person.role == "Manager":
                # FETCH: Tasks assigned to ME (person) OR tasks assigned to MY TEAM
                context["tasks"] = Task.objects.filter(
                    Q(assigned_to=person) | Q(assigned_to__manager=person)
                ).distinct()  # .distinct() prevents duplicates if logic overlaps
            else:
                # Employees only see their own tasks
                context["tasks"] = Task.objects.filter(assigned_to=person)
        else:
            context["people"] = None
            context["contracts"] = None
            context["tasks"] = None

        return context
