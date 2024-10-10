from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render
from django.views import View
from items.models import Book
from people.models import Author, Critic

from .forms import ContactForm


class ContactUsView(View):
    template_name = "form.html"

    def get(self, request):
        form = ContactForm()
        return render(request, self.template_name, {"form": form, "name": "Contact Us"})

    def notify(self, message, email, subject):
        full_message = f"""
        Received message below from {email}, {subject}
        ________________________


        {message}
        """
        send_mail(
            subject="Received contact form submission",
            message=full_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.NOTIFY_EMAIL],
        )

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            subject = form.cleaned_data.get("subject")
            message = form.cleaned_data.get("message")

            self.notify(message=message, subject=subject, email=email)

            messages.success(
                request,
                "Your contact attempt was successful, please wait for our response.",
            )
            return render(request, "success.html", {})

        messages.error(request, "Please correct the error below.")
        return render(request, self.template_name, {"form": form, "name": "Contact Us"})


def home_view(request):
    # Aggregate information for books, authors, and critics
    context = {
        "total_books": Book.objects.count(),
        "first_book_date": Book.objects.order_by("date_created")
        .values_list("date_created", flat=True)
        .first(),
        "last_book_date": Book.objects.order_by("-date_created")
        .values_list("date_created", flat=True)
        .first(),
        "total_authors": Author.objects.count(),
        "first_author_date": Author.objects.order_by("date_created")
        .values_list("date_created", flat=True)
        .first(),
        "last_author_date": Author.objects.order_by("-date_created")
        .values_list("date_created", flat=True)
        .first(),
        "total_critics": Critic.objects.count(),
        "first_critic_date": Critic.objects.order_by("date_created")
        .values_list("date_created", flat=True)
        .first(),
        "last_critic_date": Critic.objects.order_by("-date_created")
        .values_list("date_created", flat=True)
        .first(),
    }
    return render(request, "home.html", context)


def about_view(request):
    return render(request, "about.html")
