import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class ComplexPasswordValidator:
    """
    Validate that the password contains:
    - At least 8 characters
    - At least one uppercase letter
    - At least one digit
    - At least one special character
    """
    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError(
                _("The password must be at least 8 characters long."),
                code='password_too_short',
            )
        if len(password) > 80:
            raise ValidationError(
                _("The password must be no more than 80 characters long."),
                code='password_too_long',
            )
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("The password must contain at least one uppercase letter."),
                code='password_no_upper',
            )
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                _("The password must contain at least one digit."),
                code='password_no_digit',
            )
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("The password must contain at least one special character."),
                code='password_no_special',
            )

    def get_help_text(self):
        return _(
            "Your password must be at least 8 characters long and contain "
            "at least one uppercase letter, one digit, and one special character."
        )
