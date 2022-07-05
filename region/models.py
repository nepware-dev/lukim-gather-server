from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


class Region(MPTTModel):
    name = models.TextField(_("name"))
    code = models.CharField(max_length=25, null=True, blank=True, default=None)
    boundary = models.MultiPolygonField(
        _("boundary"), null=True, blank=True, default=None
    )
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        verbose_name=_("parent region"),
        null=True,
        blank=True,
        default=None,
    )

    def __str__(self):
        return self.name


class ProtectedArea(MPTTModel):
    name = models.TextField(_("name"))
    code = models.CharField(max_length=25, null=True, blank=True, default=None)
    boundary = models.MultiPolygonField(
        _("boundary"), null=True, blank=True, default=None
    )
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        verbose_name=_("parent protected area"),
        null=True,
        blank=True,
        default=None,
    )

    def __str__(self):
        return self.name
