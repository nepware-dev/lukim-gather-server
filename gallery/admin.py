from django.contrib import admin

from gallery.models import Gallery


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)
