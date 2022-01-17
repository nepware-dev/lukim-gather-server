from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from lukimgather.auth_validators import CustomASCIIUsernameValidator
from lukimgather.fields import LowerCharField, LowerEmailField
from lukimgather.managers import CustomUserManager
from lukimgather.models import TimeStampedModel


class User(AbstractUser):
    username_validator = CustomASCIIUsernameValidator

    # Abstract user modification
    username = LowerCharField(
        verbose_name=_("Username"),
        max_length=20,
        unique=True,
        help_text=_(
            "Required. Length can be between 5 to 20. Letters, digits and ./-/_ only."
        ),
        validators=[
            username_validator,
            MinLengthValidator(limit_value=5),
        ],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    email = LowerEmailField(
        verbose_name=_("Email Address"),
        unique=True,
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )
    is_active = models.BooleanField(
        verbose_name=_("Active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. Unselect this instead of deleting accounts."
        ),
    )

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if self.pk:
            cls = self.__class__
            old = cls.objects.get(pk=self.pk)
            changed_fields = []
            for field in cls._meta.get_fields():
                field_name = field.name
                try:
                    old_val = getattr(old, field_name)
                    new_val = getattr(self, field_name)
                    if hasattr(field, "is_custom_lower_field"):
                        if field.is_custom_lower_field():
                            new_val = new_val.lower()
                    if old_val != new_val:
                        changed_fields.append(field_name)
                except Exception:
                    pass
            kwargs["update_fields"] = changed_fields
        super().save(*args, **kwargs)


class PasswordResetPin(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_pin",
    )
    no_of_incorrect_attempts = models.PositiveIntegerField(
        verbose_name=_("No Of Incorrect Attempts"), default=0
    )
    pin = models.PositiveIntegerField(
        verbose_name=_("Pin"), validators=[MinLengthValidator(6), MaxLengthValidator(6)]
    )
    pin_expiry_time = models.DateTimeField(verbose_name=_("Pin Expiry Time"))
    is_active = models.BooleanField(verbose_name=_("Is Active"), default=True)
    identifier = models.CharField(verbose_name=_("Identifier"), max_length=16)


class EmailConfirmationPin(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_confirm_pin",
    )
    no_of_incorrect_attempts = models.PositiveIntegerField(
        verbose_name=_("No Of Incorrect Attempts"), default=0
    )
    pin = models.PositiveIntegerField(
        verbose_name=_("Pin"), validators=[MinLengthValidator(6), MaxLengthValidator(6)]
    )
    pin_expiry_time = models.DateTimeField(verbose_name=_("Pin Expiry Time"))
    is_active = models.BooleanField(verbose_name=_("Is Active"), default=True)


class EmailChangePin(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_change_pin",
    )
    no_of_incorrect_attempts = models.PositiveIntegerField(
        verbose_name=_("No Of Incorrect Attempts"), default=0
    )
    pin = models.PositiveIntegerField(
        verbose_name=_("Pin"), validators=[MinLengthValidator(6), MaxLengthValidator(6)]
    )
    pin_expiry_time = models.DateTimeField(verbose_name=_("Pin Expiry Time"))
    new_email = LowerEmailField()
    is_active = models.BooleanField(verbose_name=_("Is Active"), default=True)
