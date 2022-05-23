from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from mptt.admin import DraggableMPTTAdmin

from .models import Region


@admin.register(Region)
class RegionAdmin(DraggableMPTTAdmin):
    list_display = ("tree_actions", "indented_title", "code", "name", "parent")
    autocomplete_fields = ("parent",)
    search_fields = ("name",)
