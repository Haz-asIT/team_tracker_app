from django.urls import path

from .views import (
    LoginInterface,
    LogoutInterface,
    ListUsers,
    ViewUserDetails,
    UpdateUser,
    DeleteUser,
    CreateNewUser,
    ListGroups,
    GroupDetailView,
    CreateGroup,
    UpdateGroup,
    DeleteGroup,
    AuditLogListView,
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView,
    CustomPasswordChangeView,
    CustomPasswordChangeDoneView,
)

app_name = "security"

urlpatterns = [
    # Authentication
    path("login/", LoginInterface.as_view(), name="login"),
    path("logout/", LogoutInterface.as_view(), name="logout"),

    # Password Change
    path("password-change/", CustomPasswordChangeView.as_view(), name="password_change"),
    path("password-change/done/", CustomPasswordChangeDoneView.as_view(), name="password_change_done"),

    # Password Reset
    path("password-reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path("password-reset/confirm/<uidb64>/<token>/", CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("password-reset/done/", CustomPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/done/", CustomPasswordResetCompleteView.as_view(), name="password_reset_complete"),

    # Users
    path("users/", ListUsers.as_view(), name="user_list"),
    path("users/<int:pk>/", ViewUserDetails.as_view(), name="user_detail"),
    path("users/edit/<int:pk>/", UpdateUser.as_view(), name="user_edit"),
    path("users/delete/<int:pk>/", DeleteUser.as_view(), name="user_delete"),
    path("users/create/", CreateNewUser.as_view(), name="user_create"),

    # Groups
    path("groups/", ListGroups.as_view(), name="group_list"),
    path("groups/<int:pk>/", GroupDetailView.as_view(), name="group_detail"),
    path("groups/add/", CreateGroup.as_view(), name="group_add"),
    path("groups/edit/<int:pk>/", UpdateGroup.as_view(), name="group_edit"),
    path("groups/delete/<int:pk>/", DeleteGroup.as_view(), name="group_delete"),

    # Audit Logs
    path("audit_log/", AuditLogListView.as_view(), name="audit_log"),
]
