from crispy_forms.helper import FormHelper
from django import forms

from .models import Author


class AuthoFilterForm(forms.Form):
    name = forms.CharField(required=False, label="Name")
    nationality = forms.ModelChoiceField(
        queryset=Author.objects.values_list("nationality", flat=True).distinct(),
        required=False,
        label="Nationality",
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
