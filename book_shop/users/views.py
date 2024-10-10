from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View

from .forms import (
    CustomLoginForm,
    CustomPasswordChangeForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm,
    CustomUserCreationForm,
    UserUpdateForm,
)
from .models import CustomUser


@login_required
def update_profile(request):
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect("profile")
    else:
        form = UserUpdateForm(instance=request.user)

    return render(
        request,
        "form.html",
        {
            "form": form,
            "name": "Update Profile",
            "message_main": "Go back to",
            "message_link": "profile",
            "link": "profile",
        },
    )


@method_decorator(login_required, name="dispatch")
class UserProfileView(View):
    template_name = "user_profile.html"

    def get(self, request):
        user = request.user
        return render(request, self.template_name, {"user": user})


@login_required
def remove_account(request):
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been successfully removed.")
        return render(
            request,
            "success.html",
            {"message": "Your account was successfully deleted."},
        )

    return redirect("profile")


class CustomSignUpView(View):
    template_name = "form.html"
    form_class = CustomUserCreationForm
    kw = {
        "name": "Sign Up",
        "message_main": "Already have an account?",
        "message_link": "Log in here",
        "link": "login",
    }

    def get(self, request):
        form = CustomUserCreationForm()
        self.kw["form"] = form
        return render(
            request,
            self.template_name,
            self.kw,
        )

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        self.kw["form"] = form
        if form.is_valid():
            form.save()
            return redirect("login")
        else:
            messages.error(request, "Please correct the error below.")
        return render(request, self.template_name, self.kw)


class CustomLoginView(LoginView):
    template_name = "form.html"
    form_class = CustomLoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["name"] = "Login"
        context["message_main"] = "Don't have an account?"
        context["message_link"] = "Register here"
        context["link"] = "signup"
        context["message_main_2"] = "Forgot yout password?"
        context["message_link_2"] = "Reset it here"
        context["link_2"] = "password_reset"
        return context


class CustomPasswordResetView(PasswordResetView):
    template_name = "form.html"
    form_class = CustomPasswordResetForm
    email_template_name = "password_reset_email.html"
    subject_template_name = "password_reset_subject.txt"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["name"] = "Password Reset"
        return context

    def form_valid(self, form):
        super().form_valid(form)
        return render(
            self.request,
            "success.html",
            {
                "message": "Email with information about password reset was successfully sent."
            },
        )


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "form.html"
    form_class = CustomSetPasswordForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["name"] = "Set New Password"
        return context

    def form_valid(self, form):
        super().form_valid(form)
        return render(
            self.request,
            "success.html",
            {"message": "Your password has been successfully reset."},
        )


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "form.html"
    form_class = CustomPasswordChangeForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["name"] = "Set New Password"
        context["message_main"] = "Go back to"
        context["message_link"] = "profile"
        context["link"] = "profile"
        return context

    def form_valid(self, form):
        super().form_valid(form)
        return render(
            self.request,
            "success.html",
            {"message": "Your password has been successfully reset."},
        )
