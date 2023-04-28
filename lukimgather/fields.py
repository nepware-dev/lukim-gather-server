from django.core.exceptions import ValidationError
from django.db import models
from validate_email import validate_email


class LowerCharField(models.CharField):
    def get_prep_value(self, value):
        return super().get_prep_value(value).lower()

    def is_custom_lower_field(self):
        return True


class LowerEmailField(models.EmailField):
    def get_prep_value(self, value):
        return super().get_prep_value(value).lower() if value else None

    def is_custom_lower_field(self):
        return True

    def validate(self, value, model_instance):
        if not validate_email(value, check_smtp=False):
            return ValidationError("Invalid email address.")
        return super().validate(value, model_instance)
