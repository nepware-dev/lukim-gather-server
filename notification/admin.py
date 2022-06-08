from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from lukimgather.admin import UserStampedModelAdmin

from .models import Notice, Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "recipient",
        "actor",
        "action_object",
        "target",
        "notification_type",
        "has_read",
    )
    autocomplete_fields = ("recipient",)
    list_filter = (
        "has_read",
        "timestamp",
    )

    class Meta:
        verbose_name = _("notification")
        verbose_plural_name = _("notifications")


@admin.register(Notice)
class NoticeAdmin(UserStampedModelAdmin):
    list_display = (
        "title",
        "notice_type",
        "is_active",
        "created_by",
        "updated_by",
        "created_at",
        "modified_at",
    )
    search_fields = (
        "title",
        "description",
    )
    list_filter = (
        "notice_type",
        "is_active",
        "created_at",
        "modified_at",
    )
