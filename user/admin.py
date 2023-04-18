from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import gettext_lazy as _

from lukimgather.admin import UserStampedModelAdmin
from support.models import AccountDeletionRequest
from survey.models import HappeningSurvey, Survey

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


class CustomUserChangeForm(UserChangeForm):
    def clean_email(self):
        email = self.cleaned_data.get("email")
        queryset = User.objects.filter(email=email)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("This email already exists.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        queryset = User.objects.filter(phone_number=phone_number)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("This phone number already exists.")
        return phone_number


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
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

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        queryset |= self.model.objects.filter(phone_number__icontains=search_term)
        return queryset, use_distinct

    def get_deleted_objects(self, obj, request):
        (
            deleted_objects,
            model_count,
            perms_needed,
            protected,
        ) = super().get_deleted_objects(obj, request)
        happening_survey_qs = HappeningSurvey.objects.filter(created_by=obj[0])
        survey_qs = Survey.objects.filter(created_by=obj[0])
        if happening_survey_qs:
            model_count[
                HappeningSurvey._meta.verbose_name_plural
            ] = happening_survey_qs.count()
            deleted_objects += list(happening_survey_qs)
        if survey_qs:
            model_count[Survey._meta.verbose_name_plural] = survey_qs.count()
            deleted_objects += list(survey_qs)

        return deleted_objects, model_count, perms_needed, protected

    def delete_model(self, request, obj):
        account_deletion_request = AccountDeletionRequest.objects.filter(
            account=obj
        ).first()
        if account_deletion_request:
            account_deletion_request.approved_by = request.user
            account_deletion_request.save()
        return super().delete_model(request, obj)


@admin.register(Grant)
class GrantAdmin(UserStampedModelAdmin):
    search_fields = ("title",)
    autocomplete_fields = ("user",)
    list_display = (
        "title",
        "user",
    )


admin.site.register(User, CustomUserAdmin)
