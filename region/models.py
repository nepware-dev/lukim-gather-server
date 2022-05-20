from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


class Region(MPTTModel):
    name = models.TextField(_("name"))
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
