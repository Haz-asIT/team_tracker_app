import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class SpecialCharacterValidator:
    """
    Requires at least one special character.
    Example special chars: @ # $ %
    """

    def validate(self, password, user=None):
        # You can expand this set if you want
        if not re.search(r'[@#$%]', password):
            raise ValidationError(
                _("Your password must contain at least one special character (e.g. @ # $ %)."),
                code="password_no_special",
            )

    def get_help_text(self):
        return _("Your password must contain at least one special character (e.g. @ # $ %).")
