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

            return render(
                request,
                "success.html",
                {
                    "message": "Your contact attempt was successful, please wait for our response."
                },
            )
        else:
            messages.error(request, "Please correct the error below.")
        return render(request, self.template_name, {"form": form, "name": "Contact Us"})


def home_view(request):
    # Books information
    total_books = Book.objects.count()
    first_book = Book.objects.order_by("date_created").first()
    last_book = Book.objects.order_by("-date_created").first()
    first_book_date = first_book.date_created if first_book else None
    last_book_date = last_book.date_created if last_book else None

    # Authors information
    total_authors = Author.objects.count()
    first_author = Author.objects.order_by("date_created").first()
    last_author = Author.objects.order_by("-date_created").first()
    first_author_date = first_author.date_created if first_author else None
    last_author_date = last_author.date_created if last_author else None

    # Critics information
    total_critics = Critic.objects.count()
    first_critic = Critic.objects.order_by("date_created").first()
    last_critic = Critic.objects.order_by("-date_created").first()
    first_critic_date = first_critic.date_created if first_critic else None
    last_critic_date = last_critic.date_created if last_critic else None

    context = {
        "total_books": total_books,
        "first_book_date": first_book_date,
        "last_book_date": last_book_date,
        "total_authors": total_authors,
        "first_author_date": first_author_date,
        "last_author_date": last_author_date,
        "total_critics": total_critics,
        "first_critic_date": first_critic_date,
        "last_critic_date": last_critic_date,
    }

    return render(request, "home.html", context)


def about_view(request):
    return render(request, "about.html")
