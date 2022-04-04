from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from mptt.admin import DraggableMPTTAdmin

from lukimgather.admin import UserStampedModelAdmin
from survey.models import LocalEnviromentalSurvey, ProtectedAreaCategory


@admin.register(ProtectedAreaCategory)
class AreaCategoryAdmin(UserStampedModelAdmin, DraggableMPTTAdmin):
    list_display = (
        "tree_actions",
        "indented_title",
        "code",
    )
    list_display_links = ("indented_title",)


@admin.register(LocalEnviromentalSurvey)
class LocalEnviromentalSurveyAdmin(UserStampedModelAdmin):
    autocomplete_fields = ("attachment",)
    list_display = (
        "title",
        "category",
    )
    list_filter = ("category",)

    class Meta:
        verbose_name = _("Local Enviromental Survey")
