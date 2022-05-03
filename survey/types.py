from graphene_django.types import DjangoObjectType
from graphene_django_extras.paginations import LimitOffsetGraphqlPagination

from survey.models import (
    Form,
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
        description = "Type definition for a category"
        fields = "__all__"
        filter_fields = {
            "id": ("exact",),
            "title": ("icontains", "iexact"),
        }
        pagination = LimitOffsetGraphqlPagination(default_limit=100, ordering="-title")


class HappeningSurveyType(DjangoObjectType):
    class Meta:
        model = HappeningSurvey
        description = "Type definition for a happening survey"
        fields = "__all__"
        pagination = LimitOffsetGraphqlPagination(default_limit=100, ordering="-title")


class FormType(DjangoObjectType):
    class Meta:
        description = "Type definition for a survey form"
        fields = "__all__"
        model = Form
        filter_fields = {
            "id": ("exact",),
            "title": ("icontains", "iexact"),
        }
        pagination = LimitOffsetGraphqlPagination(default_limit=100, ordering="-title")


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
