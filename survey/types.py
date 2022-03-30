import graphql_geojson
from graphene_django.types import DjangoObjectType

from survey.models import LocalEnviromentalSurvey, ProtectedAreaCategory


class ProtectedAreaCategoryType(DjangoObjectType):
    class Meta:
        model = ProtectedAreaCategory
        fields = "__all__"


class LocalEnviromentalSurveyType(DjangoObjectType):
    class Meta:
        model = LocalEnviromentalSurvey
        graphql_geojson.converter = (
            "location",
            "boundary",
        )
