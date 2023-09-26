import graphene
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from graphene.types.generic import GenericScalar
from graphene_django.types import DjangoObjectType
from graphene_django_extras.paginations import LimitOffsetGraphqlPagination
from reversion.models import Version

from gallery.models import Gallery
from lukimgather.types import RevisionType
from survey.models import Form, HappeningSurvey, ProtectedAreaCategory, Survey


class ProtectedAreaCategoryType(DjangoObjectType):
    class Meta:
        model = ProtectedAreaCategory
        description = "Type definition for a category"
        fields = "__all__"
        filter_fields = {
            "id": ("exact",),
            "title": ("icontains", "iexact"),
        }
        pagination = LimitOffsetGraphqlPagination(default_limit=100, ordering="-title")


class HappeningSurveyType(DjangoObjectType):
    is_offline = graphene.Boolean()

    def resolve_is_offline(self, info):
        return False

    def resolve_audio_file(self, info):
        if self.audio_file and self.audio_file.url:
            return info.context.build_absolute_uri(self.audio_file.url)
        else:
            return None

    class Meta:
        model = HappeningSurvey
        description = "Type definition for a happening survey"
        fields = "__all__"
        pagination = LimitOffsetGraphqlPagination(default_limit=100, ordering="-title")


class HappeningSurveyHistoryVersionType(graphene.ObjectType):
    fields = graphene.Field(HappeningSurveyType)

    def resolve_fields(self, info):
        deserialized_object = list(serializers.deserialize("json", self))[0]
        happening_survey_dict = {}
        for field in HappeningSurveyType._meta.fields.keys():
            try:
                happening_survey_dict[field] = getattr(
                    deserialized_object.object, field, None
                )
            except ObjectDoesNotExist:
                happening_survey_dict[field] = None
        attachments = deserialized_object.m2m_data.get("attachment")
        if attachments:
            happening_survey_dict["attachment"] = Gallery.objects.filter(
                id__in=attachments
            )
        return HappeningSurveyType(**happening_survey_dict)


class HappeningSurveyHistoryType(DjangoObjectType):
    revision = graphene.Field(RevisionType)
    serialized_data = graphene.Field(HappeningSurveyHistoryVersionType)

    class Meta:
        model = Version
        description = "Type definition for a version"
        fields = "__all__"


class FormType(DjangoObjectType):
    xform = GenericScalar()

    class Meta:
        description = "Type definition for a survey form"
        fields = "__all__"
        model = Form
        filter_fields = {
            "id": ("exact",),
            "title": ("icontains", "iexact"),
        }
        pagination = LimitOffsetGraphqlPagination(default_limit=100, ordering="-title")


class SurveyType(DjangoObjectType):
    class Meta:
        model = Survey
        fields = "__all__"
        pagination = LimitOffsetGraphqlPagination(
            default_limit=100, ordering="-created_at"
        )
