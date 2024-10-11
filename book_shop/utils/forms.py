from crispy_forms.helper import FormHelper
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _


class ContactForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(attrs={"placeholder": "Your e-mail", "required": True}),
        help_text=_("We'll try to contact you as soon as possible."),
    )
    subject = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Subject", "required": True}),
        help_text=_("Please make it as meaningful as possible. Up to 50 signs."),
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "Your message", "required": True}),
        help_text=_("Please keep it straightforward, up to 4000 signs."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.form_id = "contact-form"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "submit_contact_form"

    def clean_email(self):
        """Validate that the email has a valid format."""
        email = self.cleaned_data.get("email").strip()

        email_validator = EmailValidator()
        try:
            email_validator(email)
        except ValidationError:
            raise ValidationError(_("Enter a valid email address."))

        return email

    def clean_subject(self):
        """Validate that the subject is not too long."""
        subject = self.cleaned_data.get("subject").strip()

        if len(subject) > 50:
            raise ValidationError(
                _("Subject is too long. Max length is 50 characters.")
            )

        return subject

    def clean_message(self):
        """Validate that the message is not too long."""
        message = self.cleaned_data.get("message").strip()

        if len(message) > 4000:
            raise ValidationError(
                _("Message is too long. Max length is 4000 characters.")
            )

        return message
