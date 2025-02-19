from django.contrib import admin
from django.db import models
from django_ckeditor_5.widgets import CKEditor5Widget


class UserStampedModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if change:
            obj.updated_by = request.user
        else:
            obj.created_by = request.user
        return super().save_model(request, obj, form, change)


class CKEditorModelAdmin(admin.ModelAdmin):
    ckeditor_fields = []

    def formfield_for_dbfield(self, db_field, request=None, **kwargs):
        if (
            isinstance(db_field, models.TextField)
            and db_field.name in self.ckeditor_fields
        ):
            kwargs["widget"] = CKEditor5Widget()
        return super().formfield_for_dbfield(db_field, request, **kwargs)
