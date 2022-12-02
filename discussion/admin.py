from django.contrib import admin
from django.utils.text import Truncator
from mptt.admin import MPTTModelAdmin

from .models import Comment, LikeComment


@admin.register(Comment)
class CommentAdmin(MPTTModelAdmin):
    list_display = (
        "created_at",
        "__str__",
        "user",
        "content_type",
        "object_id",
        "truncated_description",
    )
    search_fields = ("user__username", "content_type")
    autocomplete_fields = ("user", "parent")

    def truncated_description(self, obj):
        description = "%s" % obj.description
        return Truncator(description).chars(100)

    truncated_description.short_description = "Description"


@admin.register(LikeComment)
class LikeCommentAdmin(admin.ModelAdmin):
    list_display = ("user", "comment")
    autocomplete_fields = ("user", "comment")
