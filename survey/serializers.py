import graphene
from graphene_django.rest_framework import serializer_converter
from rest_framework import serializers

from lukimgather.serializers import UserModelSerializer
from survey.models import Form, Survey


@serializer_converter.get_graphene_type_from_serializer_field.register(
    serializers.JSONField
)
def convert_serializer_field_to_generic(field):
    return graphene.types.generic.GenericScalar


class FormSerializer(UserModelSerializer):
    class Meta:
        model = Form
        field = "__all__"


class SurveySerializer(UserModelSerializer):
    class Meta:
        model = Survey
        fields = "__all__"
