from django.contrib import admin

from gallery.models import Gallery
from lukimgather.admin import UserStampedModelAdmin


@admin.register(Gallery)
class GalleryAdmin(UserStampedModelAdmin):
    list_display = (
        "title",
        "created_at",
    )
    search_fields = ("title",)
