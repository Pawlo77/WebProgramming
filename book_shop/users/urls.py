from django.contrib.auth import views as auth_views
from django.urls import include, path

from .views import (
    CustomLoginView,
    CustomPasswordChangeView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetView,
    CustomSignUpView,
    UserProfileView,
    remove_account,
    update_profile,
)

urlpatterns = [
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("update_account/", update_profile, name="update_account"),
    path("remove_account/", remove_account, name="remove_account"),
    path("signup/", CustomSignUpView.as_view(), name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path(
        "password_change/",
        CustomPasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
