from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin

from lukimgather.admin import UserStampedModelAdmin
from support.models import EmailTemplate, Feedback, LegalDocument


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
