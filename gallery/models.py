import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from lukimgather.models import TimeStampedModel


class MediaType(models.TextChoices):
    VIDEO = "video", _("Video")
    IMAGE = "image", _("Image")
    OTHER = "other", _("Other")


class Gallery(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("Title"), max_length=255)
    type = models.CharField(
        _("Media Type"),
        max_length=15,
        choices=MediaType.choices,
        default=MediaType.IMAGE,
    )
    media = models.FileField(
        _("Media File"),
        upload_to="attachments/%Y/%m/%d/",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Gallery")
        verbose_name_plural = _("Galleries")
