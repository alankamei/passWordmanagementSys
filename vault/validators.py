import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class StrongPasswordValidator:
    """
    Requires at least one uppercase letter, one lowercase letter,
    one digit, and one special character.

    Registered in settings.AUTH_PASSWORD_VALIDATORS — Django will call
    this during registration, password change, and createsuperuser.
    """

    def validate(self, password, user=None):
        missing = []

        if not re.search(r"[A-Z]", password):
            missing.append("an uppercase letter")
        if not re.search(r"[a-z]", password):
            missing.append("a lowercase letter")
        if not re.search(r"\d", password):
            missing.append("a digit")
        if not re.search(r"[^A-Za-z0-9]", password):
            missing.append("a special character")

        if missing:
            raise ValidationError(
                _("Password must contain at least: %(missing)s."),
                code="password_too_weak",
                params={"missing": ", ".join(missing)},
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least one uppercase letter, "
            "one lowercase letter, one digit, and one special character."
        )