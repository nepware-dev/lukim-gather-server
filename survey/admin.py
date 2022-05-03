from admin_auto_filters.filters import AutocompleteFilter
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin
from mptt.admin import DraggableMPTTAdmin
from ordered_model.admin import OrderedModelAdmin

from lukimgather.admin import UserStampedModelAdmin
from survey.models import (
    Form,
    HappeningSurvey,
    Option,
    ProtectedAreaCategory,
    Question,
    QuestionGroup,
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


@admin.register(QuestionGroup)
class QuestionGroupAdmin(
    UserStampedModelAdmin,
    TranslationAdmin,
    OrderedModelAdmin,
):
    list_display = ("code", "title", "move_up_down_links")
    search_fields = (
        "code",
        "title",
    )


class OptionInline(admin.StackedInline):
    model = Option
    extra = 0


class QuestionGroupAutoCompleteFilter(AutocompleteFilter):
    title = "group"
    field_name = "group"


@admin.register(Question)
class QuestionAdmin(
    UserStampedModelAdmin,
    TranslationAdmin,
    OrderedModelAdmin,
):
    list_display = (
        "code",
        "title",
        "group",
        "answer_type",
        "is_required",
        "move_up_down_links",
    )
    list_filter = (QuestionGroupAutoCompleteFilter,)
    autocomplete_fields = ("group",)
    search_fields = (
        "code",
        "title",
    )
    inlines = (OptionInline,)


@admin.register(Option)
class OptionAdmin(
    UserStampedModelAdmin,
    TranslationAdmin,
    OrderedModelAdmin,
):
    list_display = ("code", "title", "question", "move_up_down_links")
    autocomplete_fields = ("question",)
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
    list_display = ("question", "survey", "answer")
    autocomplete_fields = ("question", "survey", "options")


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
