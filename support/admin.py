from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin
from mptt.admin import DraggableMPTTAdmin
from ordered_model.admin import OrderedModelAdmin

from lukimgather.admin import UserStampedModelAdmin
from support.models import (
    Category,
    EmailTemplate,
    Feedback,
    FrequentlyAskedQuestion,
    LegalDocument,
    Resource,
    ResourceTag,
    Tutorial,
)


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "title"
    list_display = (
        "tree_actions",
        "indented_title",
    )
    list_display_links = ("indented_title",)


@admin.register(LegalDocument)
class LegalDocumentAdmin(UserStampedModelAdmin, TranslationAdmin):
    list_display = ("document_type",)

    class Meta:
        verbose_name = _("legal document")
        verbose_plural_name = _("legal documents")


@admin.register(Feedback)
class FeedbackAdmin(UserStampedModelAdmin):
    list_display = ("title",)

    class Meta:
        verbose_name = _("feedback")
        verbose_plural_name = _("feedbacks")


@admin.register(FrequentlyAskedQuestion)
class FrequentlyAskedQuestionAdmin(
    UserStampedModelAdmin, OrderedModelAdmin, TranslationAdmin
):
    list_display = ("question", "move_up_down_links")

    class Meta:
        verbose_name = _("frequently asked question")
        verbose_plural_name = _("frequently asked questions")


@admin.register(Tutorial)
class TutorialAdmin(UserStampedModelAdmin, OrderedModelAdmin, TranslationAdmin):
    list_display = ("question", "move_up_down_links")

    class Meta:
        verbose_name = _("tutorial")
        verbose_plural_name = _("tutorials")


@admin.register(ResourceTag)
class ResourceTagAdmin(UserStampedModelAdmin, OrderedModelAdmin):
    list_display = ("title", "move_up_down_links")
    search_fields = ("title",)

    class Meta:
        verbose_name = _("resource")
        verbose_plural_name = _("resource tags")


@admin.register(Resource)
class ResourceAdmin(UserStampedModelAdmin, OrderedModelAdmin, TranslationAdmin):
    list_display = (
        "title",
        "resource_type",
        "video_url",
        "attachment",
        "move_up_down_links",
    )
    autocomplete_fields = ("tags",)

    class Meta:
        verbose_name = _("resource")
        verbose_plural_name = _("resources")


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ("identifier",)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    class Meta:
        verbose_name = _("email template")
        verbose_plural_name = _("email templates")
