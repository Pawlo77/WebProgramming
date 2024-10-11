from django.contrib.auth import views as auth_views
from django.urls import path

from .views import (
    CustomLoginView,
    CustomPasswordChangeDoneView,
    CustomPasswordChangeView,
    CustomPasswordResetCompleteView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetDoneView,
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
        CustomPasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path(
        "password_reset/done/",
        CustomPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),  # not used
]
