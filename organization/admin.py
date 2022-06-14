from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from lukimgather.admin import UserStampedModelAdmin

from .models import Organization


@admin.register(Organization)
class OrganizationAdmin(UserStampedModelAdmin):
    list_display = (
        "title",
        "acronym",
        "created_at",
    )
    search_fields = (
        "title",
        "acronym",
        "description",
    )

    class Meta:
        verbose_name = _("organization")
        verbose_plural_name = _("organizations")
