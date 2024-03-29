from ckeditor.fields import RichTextField
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import EmailValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from lukimgather.models import TimeStampedModel, UserStampedModel


class Announcement(UserStampedModel, TimeStampedModel):
    title = models.CharField(_("title"), max_length=255)
    description = RichTextField(_("description"), blank=True, null=True, default=None)
    organization = models.ManyToManyField(
        "organization.Organization", blank=True, verbose_name=_("Organizations")
    )
    user = models.ManyToManyField("user.User", blank=True, verbose_name=_("Users"))
    notify_all = models.BooleanField(default=False, verbose_name=_("Notify all"))

    def __str__(self):
        return self.title


class Notification(TimeStampedModel):
    # recipient
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="notifications",
        on_delete=models.CASCADE,
        verbose_name=_("recipient"),
    )
    has_read = models.BooleanField(
        _("read"), blank=False, default=False, editable=False, db_index=True
    )

    # actor related
    actor_content_type = models.ForeignKey(
        ContentType,
        related_name="notify_actor",
        on_delete=models.CASCADE,
        verbose_name=_("actor content type"),
    )
    actor_object_id = models.CharField(
        _("actor object id"),
        null=True,
        blank=True,
        max_length=36,
    )
    actor = GenericForeignKey("actor_content_type", "actor_object_id")

    # notification related
    verb = models.CharField(_("verb"), max_length=100)
    description = models.TextField(_("description"))
    notification_type = models.CharField(
        _("notification type"), max_length=50, default="default"
    )
    timestamp = models.DateTimeField(_("timestamp"), default=timezone.now)

    # action object related
    action_object_content_type = models.ForeignKey(
        ContentType,
        related_name="notify_action_object",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name=_("action object content type"),
    )
    action_object_object_id = models.CharField(
        _("action object object id"),
        null=True,
        blank=True,
        max_length=36,
    )
    action_object = GenericForeignKey(
        "action_object_content_type", "action_object_object_id"
    )

    # target related
    target_content_type = models.ForeignKey(
        ContentType,
        related_name="notify_target",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name=_("target content type"),
    )
    target_object_id = models.CharField(
        _("target object id"),
        null=True,
        blank=True,
        max_length=36,
    )
    target = GenericForeignKey("target_content_type", "target_object_id")

    class Meta:
        ordering = ("-created_at",)
        index_together = ("recipient", "has_read")


class Notice(UserStampedModel, TimeStampedModel):
    class NoticeTypeChoice(models.TextChoices):
        USER = "user", _("User")
        PUBLIC = "public", _("Public")

    title = models.CharField(_("title"), max_length=255)
    description = RichTextField(_("description"), blank=True, null=True, default=None)
    notice_type = models.CharField(
        _("notice type"),
        max_length=6,
        default="public",
        choices=NoticeTypeChoice.choices,
    )
    is_active = models.BooleanField(_("active"), default=True)

    def __str__(self):
        return self.title


class CategoryActivityTrigger(UserStampedModel, TimeStampedModel):
    category = models.ForeignKey(
        "survey.ProtectedAreaCategory",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="category_activity_triggers",
    )


class ContactEmail(UserStampedModel, TimeStampedModel):
    email = models.EmailField(max_length=254, validators=[EmailValidator])
    category_activity_trigger = models.ForeignKey(
        "CategoryActivityTrigger",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="contact_emails",
    )
