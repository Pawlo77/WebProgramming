from datetime import date

from crispy_forms.helper import FormHelper
from django import forms

from .models import Book


class BookFilterForm(forms.Form):
    title = forms.CharField(required=False, label="Title")
    author = forms.ModelChoiceField(
        queryset=Book.objects.values_list("author", flat=True).distinct(),
        required=False,
        label="Author",
    )
    date_published = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Date Published",
    )
    language = forms.CharField(required=False, label="Language")
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
