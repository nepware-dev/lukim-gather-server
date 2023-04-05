from ckeditor.fields import RichTextField
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from lukimgather.auth_validators import CustomASCIIUsernameValidator
from lukimgather.fields import LowerCharField, LowerEmailField
from lukimgather.managers import CustomUserManager
from lukimgather.models import TimeStampedModel, UserStampedModel

from .tasks import send_user_mail, send_user_sms


class User(AbstractUser):
    class Gender(models.TextChoices):
        MALE = "M", _("Male")
        FEMALE = "F", _("Female")
        OTHER = "O", _("Other")

    username_validator = CustomASCIIUsernameValidator

    # Abstract user modification
    username = LowerCharField(
        verbose_name=_("Username"),
        max_length=40,
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
        error_messages={
            "unique": _("A user with that email already exists."),
        },
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(
        verbose_name=_("Active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. Unselect this instead of deleting accounts."
        ),
    )
    organization = models.CharField(
        _("organization"), max_length=255, null=True, blank=True, default=None
    )
    avatar = models.ImageField(
        verbose_name=_("Avatar"),
        upload_to="user/images",
        null=True,
        blank=True,
        default=None,
    )
    phone_number = PhoneNumberField(blank=True, null=True)
    gender = models.CharField(
        blank=True,
        null=True,
        max_length=1,
        choices=Gender.choices,
        default=None,
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

    def notify(
        self,
        actor,
        verb,
        notification_type=None,
        timestamp=timezone.now(),
        action_object=None,
        target=None,
        description=None,
    ):
        """
        Create notification for user.
        Notifications are actually actions events, which are categorized by four main components.
        Actor. The object that performed the activity.
        Verb. The verb phrase that identifies the action of the activity.
        Action Object. (Optional) The object linked to the action itself.
        Target. (Optional) The object to which the activity was performed.
        Actor, Action Object and Target are GenericForeignKeys to any arbitrary Django object.
        An action is a description of an action that was performed (Verb) at some instant in time by some Actor on some
        optional Target that results in an Action Object getting created/updated/deleted
        Use '{actor} {verb} {action_object(optional)} on {target(optional)}' as description if description is not provided
        """
        if not description:
            extra_content = ""
            if action_object:
                extra_content += f" {action_object}"
            if target:
                extra_content += f" on {target}"
            description = f"{actor} {verb}{extra_content}"

        NotificationModel = apps.get_model("notification", "Notification")
        NotificationModel.objects.create(
            recipient=self,
            actor=actor,
            verb=verb,
            description=description,
            notification_type=notification_type,
            timestamp=timestamp,
            action_object=action_object,
            target=target,
        )

    def celery_email_user(self, subject, message, from_email=None, **kwargs):
        if settings.ENABLE_CELERY:
            send_user_mail.delay(
                self.pk, subject, message, from_email=from_email, **kwargs
            )
        else:
            self.email_user(subject, message, from_email=from_email, **kwargs)

    def celery_sms_user(self, to, message, **kwargs):
        if settings.ENABLE_SNS:
            send_user_sms.delay(to=to, message=message)


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


class PhoneNumberConfirmationPin(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="phone_number_confirm_pin",
    )
    no_of_incorrect_attempts = models.PositiveIntegerField(
        verbose_name=_("No Of Incorrect Attempts"), default=0
    )
    pin = models.PositiveIntegerField(
        verbose_name=_("Pin"), validators=[MinLengthValidator(6), MaxLengthValidator(6)]
    )
    pin_expiry_time = models.DateTimeField(verbose_name=_("Pin Expiry Time"))
    is_active = models.BooleanField(verbose_name=_("Is Active"), default=True)


class PhoneNumberChangePin(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="phone_number_change_pin",
    )
    no_of_incorrect_attempts = models.PositiveIntegerField(
        verbose_name=_("No Of Incorrect Attempts"), default=0
    )
    pin = models.PositiveIntegerField(
        verbose_name=_("Pin"), validators=[MinLengthValidator(6), MaxLengthValidator(6)]
    )
    pin_expiry_time = models.DateTimeField(verbose_name=_("Pin Expiry Time"))
    new_phone_number = PhoneNumberField(default=None)
    is_active = models.BooleanField(verbose_name=_("Is Active"), default=True)


class Grant(UserStampedModel, TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="grant",
    )
    title = models.CharField(_("title"), max_length=255)
    description = RichTextField(_("description"), null=True, blank=True, default=None)
    organization = models.ManyToManyField(
        "organization.Organization", blank=True, verbose_name=_("Organizations")
    )

    def __str__(self):
        return self.title
