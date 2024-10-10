from datetime import date

from crispy_forms.helper import FormHelper
from django import forms
from people.models import Author

from .models import Book


class BookFilterForm(forms.Form):
    title = forms.CharField(required=False, label="Title", help_text="Book title.")
    author = forms.ModelChoiceField(
        queryset=Author.objects.order_by("last_name", "first_name"),
        required=False,
        label="Author",
        widget=forms.Select(attrs={"class": "form-control"}),
        help_text="Book's author.",
    )
    date_published = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Date Published",
        help_text="Book's publication date.",
    )
    language = forms.CharField(
        required=False, label="Language", help_text="Book's original language."
    )
    rating = forms.ChoiceField(
        choices=[
            ("", "All"),
            ("1", "1 Star"),
            ("2", "2 Stars"),
            ("3", "3 Stars"),
            ("4", "4 Stars"),
            ("5", "5 Stars"),
        ],
        required=False,
        label="Rating",
        help_text="Book's rating.",
    )

    def clean_date_published(self):
        """Makes sure that date_published is from past"""
        date_published = self.cleaned_data.get("date_published")
        if date_published:
            if date_published > date.today():
                self.add_error(
                    "date_published", _("Invalid published date - date from a future.")
                )
        return date_published

    def clean_language(self):
        """Strips language"""
        language = self.cleaned_data.get("language")
        if language:
            return language.strip()
        return language

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.form_id = "filter-books-form"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "login"

        self.fields["author"].label_from_instance = (
            lambda obj: f"{obj.first_name} {obj.last_name}"
        )
