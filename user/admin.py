from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from lukimgather.admin import UserStampedModelAdmin

from .models import Grant, User

ADDITIONAL_USER_FIELDS = (
    (
        _("Additional Fields"),
        {
            "fields": (
                "gender",
                "phone_number",
                "organization",
                "avatar",
            )
        },
    ),
)


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + ADDITIONAL_USER_FIELDS
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


@admin.register(Grant)
class GrantAdmin(UserStampedModelAdmin):
    search_fields = ("title",)
    autocomplete_fields = ("user",)
    list_display = (
        "title",
        "user",
    )


admin.site.register(User, CustomUserAdmin)
