from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from mptt.admin import DraggableMPTTAdmin
from ordered_model.admin import OrderedModelAdmin

from lukimgather.admin import UserStampedModelAdmin
from region.models import Region
from survey.models import Form, HappeningSurvey, ProtectedAreaCategory, Survey


@admin.register(Form)
class FormAdmin(UserStampedModelAdmin, OrderedModelAdmin):
    list_display = (
        "code",
        "title",
        "description",
    )
    list_filter = ("created_at",)
    search_fields = (
        "code",
        "title",
        "description",
    )
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(Survey)
class SurveyAdmin(UserStampedModelAdmin, OrderedModelAdmin):
    list_display = ("title", "move_up_down_links")
    list_filter = ("created_at",)
    search_fields = ("title",)


@admin.register(ProtectedAreaCategory)
class AreaCategoryAdmin(UserStampedModelAdmin, DraggableMPTTAdmin):
    list_display = (
        "tree_actions",
        "indented_title",
        "code",
    )
    list_display_links = ("indented_title",)


@admin.register(HappeningSurvey)
class HappeningSurveyAdmin(UserStampedModelAdmin):
    autocomplete_fields = ("attachment",)
    list_display = (
        "title",
        "category",
        "sentiment",
        "improvement",
        "status",
        "is_public",
        "is_test",
        "created_at",
    )
    list_filter = (
        "category",
        "created_at",
        "improvement",
        "is_public",
        "is_test",
        "status",
    )
    search_fields = (
        "title",
        "category__title",
        "description",
        "location",
        "boundary",
        "region__name",
    )

    def save_model(self, request, obj, form, change):
        region_geo = obj.location if obj.location else obj.boundary
        survey_region = (
            Region.objects.filter(boundary__bbcontains=region_geo).first()
            if region_geo
            else None
        )
        if obj.region != survey_region:
            obj.region = survey_region
        super().save_model(request, obj, form, change)
