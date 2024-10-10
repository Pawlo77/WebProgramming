from datetime import date

from crispy_forms.helper import FormHelper
from django import forms

from .models import Author, Critic


class AuthorFilterForm(forms.Form):
    name = forms.CharField(
        required=False,
        label="Name",
        help_text="Author's name.",
    )
    nationality = forms.ChoiceField(
        choices=[
            (nationality, nationality)
            for nationality in Author.objects.values_list("nationality", flat=True)
            .distinct()
            .order_by("nationality")
        ],
        required=False,
        label="Nationality",
        widget=forms.Select(attrs={"class": "form-control"}),
        help_text="Author's nationality.",
    )
    birth_year = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "YYYY",
                "pattern": "[0-9]{4}",
                "title": "Enter a valid year",
            }
        ),
        label="Birth Year",
        max_length=4,
        help_text="Author's birth year.",
    )
    website = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={
                "placeholder": "https://example.com",
            }
        ),
        label="Website",
        help_text="Author's official website or portfolio link.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.form_id = "filter-books-form"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "login"

    def clean_birth_year(self):
        """Makes sure that birth_year is from past"""
        birth_year = self.cleaned_data.get("birth_year")
        if birth_year:
            birth_year = int(birth_year)
            if birth_year > date.today().year:
                self.add_error(
                    "birth_year", _("Invalid birth year - date from a future.")
                )
        return birth_year

    def clean_name(self):
        """Strips name"""
        name = self.cleaned_data.get("name")
        if name:
            return name.strip()
        return name


class CriticFilterForm(forms.Form):
    name = forms.CharField(
        required=False,
        label="Name",
        help_text="Critic's name.",
    )
    nationality = forms.ChoiceField(
        choices=[
            (nationality, nationality)
            for nationality in Critic.objects.values_list("nationality", flat=True)
            .distinct()
            .order_by("nationality")
        ],
        required=False,
        label="Nationality",
        widget=forms.Select(attrs={"class": "form-control"}),
        help_text="Critic's nationality.",
    )
    birth_year = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "YYYY",
                "pattern": "[0-9]{4}",
                "title": "Enter a valid year",
            }
        ),
        label="Birth Year",
        max_length=4,
        help_text="Critic's birth date.",
    )
    website = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={
                "placeholder": "https://example.com",
            }
        ),
        label="Website",
        help_text="Critic's official website or portfolio link.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.form_id = "filter-books-form"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "login"

    def clean_birth_year(self):
        """Makes sure that birth_year is from past"""
        birth_year = self.cleaned_data.get("birth_year")
        if birth_year:
            birth_year = int(birth_year)
            if birth_year > date.today().year:
                self.add_error(
                    "birth_year", _("Invalid birth year - date from a future.")
                )
        return birth_year

    def clean_name(self):
        """Strips name"""
        name = self.cleaned_data.get("name")
        if name:
            return name.strip()
        return name
