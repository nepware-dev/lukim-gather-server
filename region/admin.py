from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from mptt.admin import DraggableMPTTAdmin

from .models import ProtectedArea, Region


@admin.register(Region)
class RegionAdmin(DraggableMPTTAdmin):
    list_display = ("tree_actions", "indented_title", "code", "name", "parent")
    autocomplete_fields = ("parent",)
    search_fields = ("name",)


@admin.register(ProtectedArea)
class ProtectedAreaAdmin(DraggableMPTTAdmin):
    list_display = ("tree_actions", "indented_title", "code", "name", "parent")
    autocomplete_fields = ("parent",)
    search_fields = ("name",)
