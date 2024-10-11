from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.shortcuts import redirect, render
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


@method_decorator(login_required, name="dispatch")
class UserProfileView(View):
    template_name = "user_profile.html"

    def get(self, request):
        return render(request, self.template_name, {"user": request.user})


@login_required
def update_profile(request):
    form = UserUpdateForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your profile has been updated successfully.")
        return redirect("profile")

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

    def get_context(self, form=None):
        return {
            "form": form or self.form_class(),
            "name": "Sign Up",
            "message_main": "Already have an account?",
            "message_link": "Log in here",
            "link": "login",
        }

    def get(self, request):
        return render(request, self.template_name, self.get_context())

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been created successfully!")
            return redirect("login")
        else:
            messages.error(request, "Please correct the error below.")

        return render(request, self.template_name, self.get_context(form))


class CustomLoginView(LoginView):
    template_name = "form.html"
    form_class = CustomLoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "name": "Login",
                "message_main": "Don't have an account?",
                "message_link": "Register here",
                "link": "signup",
                "message_main_2": "Forgot your password?",
                "message_link_2": "Reset it here",
                "link_2": "password_reset",
            }
        )
        return context


class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = "success.html"


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "success.html"


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "success.html"


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
        messages.success(
            self.request,
            "Email with information about password reset was successfully sent.",
        )
        return redirect("login")


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "form.html"
    form_class = CustomSetPasswordForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["name"] = "Set New Password"
        return context

    def form_valid(self, form):
        super().form_valid(form)
        messages.success(self.request, "Your password has been successfully reset.")
        return redirect("login")

        # Check if the link (token) is valid or not
        response = super().dispatch(request, *args, **kwargs)
        if not self.validlink:
            messages.error(self.request, "The password reset link is no longer valid.")
            return render(request, "home.html")
        return response


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "form.html"
    form_class = CustomPasswordChangeForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "name": "Set New Password",
                "message_main": "Go back to",
                "message_link": "profile",
                "link": "profile",
            }
        )
        return context

    def form_valid(self, form):
        super().form_valid(form)
        messages.success(self.request, "Your password has been successfully changed.")
        return redirect("profile")
