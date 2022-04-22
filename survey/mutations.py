import graphene
import graphql_geojson
from graphene.types.generic import GenericScalar
from graphene_django.rest_framework.mutation import SerializerMutation
from graphql_jwt.decorators import login_required

from survey.models import HappeningSurvey
from survey.serializers import (
    OptionSerializer,
    QuestionGroupSerializer,
    QuestionSerializer,
    SurveyAnswerSerializer,
    SurveySerializer,
    WritableSurveyAnswerSerializer,
)
from survey.types import HappeningSurveyType


class QuestionGroupMutation(SerializerMutation):
    class Meta:
        serializer_class = QuestionGroupSerializer


class QuestionMutation(SerializerMutation):
    class Meta:
        serializer_class = QuestionSerializer
        convert_choices_to_enum = False


class OptionMutation(SerializerMutation):
    class Meta:
        serializer_class = OptionSerializer


class SurveyMutation(SerializerMutation):
    class Meta:
        serializer_class = SurveySerializer


class SurveyAnswerMutation(SerializerMutation):
    class Meta:
        serializer_class = SurveyAnswerSerializer
        convert_choices_to_enum = False


class WritableSurveyAnswerMutation(SerializerMutation):
    class Meta:
        serializer_class = SurveyAnswerSerializer


class HappeningSurveyInput(graphene.InputObjectType):
    category_id = graphene.Int(description="category id", required=True)
    title = graphene.String(description="title", required=True)
    description = graphene.String(description="description", required=False)
    sentiment = graphene.String(description="Sentiment", required=False)
    attachment = graphene.List(graphene.ID, description="attachments", required=False)
    location = graphql_geojson.Geometry(required=False)
    boundary = graphql_geojson.Geometry(required=False)


class CreateHappeningSurvey(graphene.Mutation):
    class Arguments:
        data = HappeningSurveyInput(
            description="Fields required to create a happening survey.",
            required=True,
        )

    errors = GenericScalar()
    result = graphene.Field(HappeningSurveyType)
    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, data):
        survey = HappeningSurvey.objects.create(
            category_id=data.category_id,
            title=data.title,
            description=data.description,
            sentiment=data.sentiment,
            location=data.location,
            boundary=data.boundary,
        )
        if data.attachment:
            survey.attachment.add(*data.attachment)
            survey.save()
        return CreateHappeningSurvey(result=survey, ok=True, errors=None)
