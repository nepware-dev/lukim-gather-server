import uuid

from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.gis.db.models import MultiPolygonField, PointField
from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from ordered_model.models import OrderedModel

from lukimgather.models import CodeModel, TimeStampedModel, UserStampedModel


class Form(CodeModel, UserStampedModel, TimeStampedModel, OrderedModel):
    title = models.CharField(_("title"), max_length=255)
    description = RichTextUploadingField(
        _("description"), blank=True, null=True, default=None
    )
    xform = models.JSONField(_("XForms"), blank=True, default=dict)

    def __str__(self):
        return self.code + "-" + self.title

    class Meta(OrderedModel.Meta):
        verbose_name = _("Form")
        verbose_name_plural = _("Forms")


class Survey(UserStampedModel, TimeStampedModel):
    title = models.CharField(_("title"), max_length=255)
    answer = models.JSONField(_("answer"), blank=True, default=dict)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Survey")
        verbose_name_plural = _("Surveys")


class ProtectedAreaCategory(MPTTModel, TimeStampedModel, UserStampedModel, CodeModel):
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
        verbose_name = _("Protected area category")
        verbose_name_plural = _("Protected area categories")


class Status(models.TextChoices):
    APPROVED = "approved", _("Approved")
    REJECTED = "rejected", _("Rejected")
    PENDING = "pending", _("Pending")


class Improvement(models.TextChoices):
    INCREASING = "increasing", _("Increasing")
    SAME = "same", _("Same")
    DECREASING = "decreasing", _("Decreasing")


class HappeningSurvey(TimeStampedModel, UserStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        "ProtectedAreaCategory",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="happening_survey",
    )
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
        verbose_name=_("Happening Survey Answer Status"),
        max_length=11,
        default=Status.PENDING,
        choices=Status.choices,
    )
    improvement = models.CharField(
        verbose_name=_("Happening Survey Improvement Status"),
        max_length=11,
        null=True,
        blank=True,
        default=None,
        choices=Improvement.choices,
    )
    region = models.ForeignKey(
        "region.Region",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="happening_survey",
    )
    is_public = models.BooleanField(default=True)
    is_test = models.BooleanField(default=False)
    data_dump = models.JSONField(blank=True, default=dict)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Happening survey")
        verbose_name_plural = _("Happening surveys")
