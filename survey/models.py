import uuid

from django.contrib.gis.db.models import MultiPolygonField, PointField
from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from lukimgather.models import TimeStampedModel, UserStampedModel


class ProtectedAreaCategory(MPTTModel, TimeStampedModel, UserStampedModel):
    title = models.CharField(_("Title"), max_length=255)
    description = models.TextField(
        _("Description"), null=True, blank=True, default=None
    )
    parent = TreeForeignKey(
        "self", blank=True, null=True, related_name="child", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.title

    class MPTTMeta:
        order_insertion_by = ["title"]

    class Meta:
        verbose_name_plural = _("Protected area categories")


class Status(models.TextChoices):
    APPROVED = "approved", _("Approved")
    REJECTED = "rejected", _("Rejected")
    PENDING = "pending", _("Pending")


class LocalEnviromentalSurvey(TimeStampedModel, UserStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        _("title"), max_length=255, null=True, blank=True, default=None
    )
    description = models.TextField(
        _("Description"), null=True, blank=True, default=None
    )
    sentiment = models.TextField(_("Sentiments"), blank=True, null=True, default=None)
    attachment = models.ManyToManyField(
        "gallery.Gallery", blank=True, verbose_name=_("Attachments")
    )
    location = PointField(_("Location"), null=True, blank=True, default=None)
    boundary = MultiPolygonField(
        _("Location Boundary"), null=True, blank=True, default=None
    )
    status = models.CharField(
        verbose_name=_("Survey Answer Status"),
        max_length=11,
        default=Status.PENDING,
        choices=Status.choices,
    )
    data_dump = models.JSONField(blank=True, default=dict)

    def __str__(self):
        return self.title
