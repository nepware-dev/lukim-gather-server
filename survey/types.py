import graphql_geojson
from graphene_django.types import DjangoObjectType

from survey.models import (
    HappeningSurvey,
    Option,
    ProtectedAreaCategory,
    Question,
    QuestionGroup,
    Survey,
    SurveyAnswer,
)


class ProtectedAreaCategoryType(DjangoObjectType):
    class Meta:
        model = ProtectedAreaCategory
        fields = "__all__"


class HappeningSurveyType(DjangoObjectType):
    class Meta:
        model = HappeningSurvey
        graphql_geojson.converter = (
            "location",
            "boundary",
        )


class OptionType(DjangoObjectType):
    class Meta:
        model = Option


class QuestionGroupType(DjangoObjectType):
    class Meta:
        model = QuestionGroup


class QuestionType(DjangoObjectType):
    class Meta:
        model = Question


class SurveyType(DjangoObjectType):
    class Meta:
        model = Survey


class SurveyAnswerType(DjangoObjectType):
    class Meta:
        model = SurveyAnswer
