from admin_auto_filters.filters import AutocompleteFilter
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from ordered_model.admin import OrderedModelAdmin

from lukimgather.admin import UserStampedModelAdmin

from .models import Project, ProjectUser


class OrganizationAutoCompleteFilter(AutocompleteFilter):
    title = "Organization"
    field_name = "organization"


class ProjectUserInline(admin.TabularInline):
    model = ProjectUser
    autocomplete_fields = ("user",)


@admin.register(Project)
class ProjectAdmin(UserStampedModelAdmin, OrderedModelAdmin):
    inlines = [ProjectUserInline]
    list_display = (
        "title",
        "organization",
        "created_at",
        "created_by",
        "move_up_down_links",
    )
    list_filter = (OrganizationAutoCompleteFilter,)
    autocomplete_fields = ("organization", "users")
    search_fields = ("title",)

    class Meta:
        verbose_name = _("project")
        verbose_plural_name = _("projects")


@admin.register(ProjectUser)
class ProjectUserAdmin(UserStampedModelAdmin):
    list_display = ("project", "user")
    autocomplete_fields = ("project", "user")

    class Meta:
        verbose_name = _("project user")
        verbose_plural_name = _("project users")
