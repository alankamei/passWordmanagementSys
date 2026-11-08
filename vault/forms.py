from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import VaultEntry


class RegisterForm(UserCreationForm):
    """Creates a new user. Password is hashed by Django with Argon2."""

    class Meta:
        model = User
        fields = ["username", "password1", "password2"]


class VaultEntryForm(forms.ModelForm):
    """
    Form for creating / editing a vault entry.

    `password` is NOT a model field — it's a plain-text input the
    user fills in, which the view encrypts before saving.
    """

    password = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
        help_text="Shown as plain text so you can verify it before saving.",
    )

    class Meta:
        model = VaultEntry
        fields = ["website", "username", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }