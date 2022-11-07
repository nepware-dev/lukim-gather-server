from ckeditor.fields import RichTextField
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from lukimgather.fields import LowerEmailField
from lukimgather.models import TimeStampedModel, UserStampedModel


class Organization(UserStampedModel, TimeStampedModel):
    title = models.CharField(_("title"), max_length=255, unique=True)
    acronym = models.CharField(
        _("acronym"), max_length=50, null=True, blank=True, default=None
    )
    description = RichTextField(_("description"), null=True, blank=True, default=None)
    email = LowerEmailField(
        verbose_name=_("Email Address"),
        blank=True,
        null=True,
    )
    logo = models.ImageField(
        _("logo"),
        upload_to="organization/organization/logos",
        null=True,
        blank=True,
        default=None,
    )
    point_of_contact = models.TextField(
        _("point of contact"), null=True, blank=True, default=None
    )
    phone_number = PhoneNumberField(blank=True, null=True)
    website = models.URLField(_("website"), blank=True, null=True, max_length=200)
    address = models.TextField(_("Address"), blank=True, null=True, max_length=255)

    def __str__(self):
        return self.title
