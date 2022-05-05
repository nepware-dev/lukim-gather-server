from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from ordered_model.admin import OrderedModelAdmin

from lukimgather.admin import UserStampedModelAdmin
from survey.models import (
    Form,
    HappeningSurvey,
    ProtectedAreaCategory,
    Survey,
    SurveyAnswer,
)


@admin.register(Form)
class FormAdmin(UserStampedModelAdmin, OrderedModelAdmin):
    list_display = (
        "code",
        "title",
    )
    search_fields = (
        "code",
        "title",
    )


@admin.register(Survey)
class SurveyAdmin(UserStampedModelAdmin, OrderedModelAdmin):
    list_display = ("title", "move_up_down_links")
    search_fields = ("title",)


@admin.register(SurveyAnswer)
class SurveyAnswerAdmin(UserStampedModelAdmin):
    list_display = ("survey", "answer")
    autocomplete_fields = ("survey",)


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
    )
    list_filter = ("category",)
