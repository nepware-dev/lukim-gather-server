from django.contrib import admin, messages
from django.contrib.admin.utils import NestedObjects, model_ngettext, quote
from django.core.exceptions import PermissionDenied
from django.db import models, router
from django.shortcuts import render
from django.urls import NoReverseMatch, reverse
from django.utils.html import format_html
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _
from django_json_widget.widgets import JSONEditorWidget
from mptt.admin import DraggableMPTTAdmin
from ordered_model.admin import OrderedModelAdmin

from lukimgather.admin import UserStampedModelAdmin
from region.models import Region
from survey.models import Form, HappeningSurvey, ProtectedAreaCategory, Survey


@admin.register(Form)
class FormAdmin(UserStampedModelAdmin, OrderedModelAdmin):
    list_display = (
        "code",
        "title",
        "description",
        "created_at",
        "created_by",
        "updated_by",
    )
    list_filter = ("created_at",)
    search_fields = (
        "code",
        "title",
        "description",
    )
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(Survey)
class SurveyAdmin(UserStampedModelAdmin):
    list_display = (
        "title",
        "created_at",
        "created_by",
        "updated_by",
    )
    list_filter = ("created_at",)
    search_fields = ("title",)


@admin.register(ProtectedAreaCategory)
class AreaCategoryAdmin(UserStampedModelAdmin, DraggableMPTTAdmin):
    list_display = (
        "tree_actions",
        "indented_title",
        "code",
    )
    list_display_links = ("indented_title",)


@admin.register(HappeningSurvey)
class HappeningSurveyAdmin(UserStampedModelAdmin):
    autocomplete_fields = ("attachment",)
    actions = [
        "approve_reject_happening_survey",
    ]
    list_display = (
        "title",
        "category",
        "region",
        "sentiment",
        "improvement",
        "status",
        "is_public",
        "is_test",
        "created_at",
        "created_by",
        "updated_by",
    )
    list_filter = (
        "category",
        "region",
        "created_at",
        "improvement",
        "is_public",
        "is_test",
        "status",
    )
    search_fields = (
        "title",
        "category__title",
        "description",
        "location",
        "boundary",
        "region__name",
    )

    def save_model(self, request, obj, form, change):
        region_geo = obj.location if obj.location else obj.boundary
        survey_region = (
            Region.objects.filter(boundary__bbcontains=region_geo).first()
            if region_geo
            else None
        )
        if obj.region != survey_region:
            obj.region = survey_region
        super().save_model(request, obj, form, change)

    @admin.action(
        permissions=["change"],
        description=_("Approve/Reject selected %(verbose_name_plural)s"),
    )
    def approve_reject_happening_survey(modeladmin, request, queryset):
        def get_selected_objects(objs, request, admin_site):
            try:
                obj = objs[0]
            except IndexError:
                return [], {}, set(), []
            else:
                using = router.db_for_write(obj._meta.model)
            collector = NestedObjects(using=using)
            collector.collect(objs)
            perms_needed = set()

            def format_callback(obj):
                model = obj.__class__
                has_admin = model in admin_site._registry
                opts = obj._meta

                no_edit_link = "%s: %s" % (capfirst(opts.verbose_name), obj)

                if has_admin:
                    if not admin_site._registry[model].has_change_permission(
                        request, obj
                    ):
                        perms_needed.add(opts.verbose_name)
                    try:
                        admin_url = reverse(
                            "%s:%s_%s_change"
                            % (admin_site.name, opts.app_label, opts.model_name),
                            None,
                            (quote(obj.pk),),
                        )
                    except NoReverseMatch:
                        return no_edit_link

                    return format_html(
                        '{}: <a href="{}">{}</a>',
                        capfirst(opts.verbose_name),
                        admin_url,
                        obj,
                    )
                else:
                    return no_edit_link

            to_change = collector.nested(format_callback)

            protected = [format_callback(obj) for obj in collector.protected]
            model_count = {
                model._meta.verbose_name_plural: len(objs)
                for model, objs in collector.model_objs.items()
            }

            return to_change, model_count, perms_needed, protected

        (
            selected_objects,
            model_count,
            perms_needed,
            protected,
        ) = get_selected_objects(queryset, request, modeladmin.admin_site)
        opts = modeladmin.model._meta
        objects_name = model_ngettext(queryset)

        if "_approved" in request.POST or "_rejected" in request.POST:
            if perms_needed:
                return PermissionDenied
            if request.POST.get("_approved"):
                queryset.update(status="approved")
            elif request.POST.get("_rejected"):
                queryset.update(status="rejected")
            n = queryset.count()
            if n:
                modeladmin.message_user(
                    request,
                    _("Successfully executed action on %(count)d %(items)s.")
                    % {"count": n, "items": model_ngettext(modeladmin.opts, n)},
                    messages.SUCCESS,
                )
            return None
        else:
            return render(
                request,
                "admin/accept_reject_bulk_action.html",
                context={
                    **modeladmin.admin_site.each_context(request),
                    "model_count": dict(model_count).items(),
                    "objects_name": str(objects_name),
                    "perms_lacking": perms_needed,
                    "queryset": queryset,
                    "selected_objects": [selected_objects],
                    "opts": opts,
                    "protected": protected,
                },
            )
