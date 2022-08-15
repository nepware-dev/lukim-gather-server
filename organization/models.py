from ckeditor.fields import RichTextField
from django.db import models
from django.utils.translation import gettext_lazy as _

from lukimgather import settings
from lukimgather.models import TimeStampedModel, UserStampedModel


class Organization(UserStampedModel, TimeStampedModel):
    title = models.CharField(_("title"), max_length=255, unique=True)
    acronym = models.CharField(
        _("acronym"), max_length=50, null=True, blank=True, default=None
    )
    description = RichTextField(_("description"), null=True, blank=True, default=None)
    logo = models.ImageField(
        _("logo"),
        upload_to="organization/organization/logos",
        null=True,
        blank=True,
        default=None,
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="member_organizations",
        blank=True,
        verbose_name=_("members"),
    )

    def __str__(self):
        return self.title
