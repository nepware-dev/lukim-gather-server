from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from lukimgather.models import TimeStampedModel


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
    actor_object_id = models.PositiveIntegerField(
        _("actor object id"), null=True, blank=True
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
    action_object_object_id = models.PositiveIntegerField(
        _("action object object id"), null=True, blank=True
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
    target_object_id = models.PositiveIntegerField(
        _("target object id"), null=True, blank=True
    )
    target = GenericForeignKey("target_content_type", "target_object_id")

    class Meta:
        ordering = ("-created_at",)
        index_together = ("recipient", "has_read")
