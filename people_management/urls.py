from django.urls import path
from . import views  

app_name = "people_management"

urlpatterns = [
    # --- ADMIN / HR ACCESS (RBAC: Admin Role) ---
    path('all/', views.ListPeople.as_view(), name='people'),
    path("people/<int:pk>/", views.ViewPersonDetails.as_view(), name="view_person_details"),
    path('create/', views.CreateNewPerson.as_view(), name='create_new_person'),
    path('<int:pk>/edit/', views.UpdatePerson.as_view(), name='update_person'),
    path('delete-profile/<int:pk>/', views.DeletePerson.as_view(), name='delete_person'),


    # --- USER SELF-SERVICE (RBAC: Normal User Role) ---
    path('my-profile/', views.ViewOwnPerson.as_view(), name='view_own_person'),
    path('my-profile/edit/', views.edit_own_person, name='edit_own_person'),
    


    # --- CONTRACT MANAGEMENT (System Admin + HR Admin) ---
    path('contracts/', views.FilteredContractListView.as_view(), name='contracts'),
    path('contract/<int:pk>/', views.ViewContractDetails.as_view(), name='contract_detail'),
    path('contract/create/', views.CreateNewContract.as_view(), name='create_contract'),
    path('contract/edit/<int:pk>/', views.UpdateContract.as_view(), name='update_contract'),
    path('contract/delete/<int:pk>/', views.DeleteContract.as_view(), name='delete_contract'),
]