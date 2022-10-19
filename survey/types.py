import graphene
from graphene.types.generic import GenericScalar
from graphene_django.types import DjangoObjectType
from graphene_django_extras.paginations import LimitOffsetGraphqlPagination

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

    class Meta:
        model = HappeningSurvey
        description = "Type definition for a happening survey"
        fields = "__all__"
        pagination = LimitOffsetGraphqlPagination(default_limit=100, ordering="-title")


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
        pagination = LimitOffsetGraphqlPagination(default_limit=100, ordering="-title")
