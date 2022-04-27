import ast

import graphene
import graphql_geojson
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from graphene.types.generic import GenericScalar
from graphene_django.rest_framework.mutation import SerializerMutation
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import login_required

from gallery.models import Gallery
from survey.models import HappeningSurvey, Option, Question, Survey, SurveyAnswer
from survey.serializers import (
    OptionSerializer,
    QuestionGroupSerializer,
    QuestionSerializer,
    SurveyAnswerSerializer,
    SurveySerializer,
    WritableSurveySerializer,
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


class WritableSurveyMutation(SerializerMutation):
    class Meta:
        serializer_class = WritableSurveySerializer
        convert_choices_to_enum = False

    @classmethod
    def mutate(cls, root, info, input):
        answers = input.pop("answers", [])
        try:
            with transaction.atomic():
                survey = Survey.objects.create(**input, created_by=info.context.user)
                for answer in answers:
                    options = answer.pop("options", None)
                    answer["question"] = Question.objects.get(id=answer["question"])
                    survey_answer = SurveyAnswer.objects.create(
                        **answer, created_by=info.context.user, survey=survey
                    )
                    if options:
                        options = ast.literal_eval(options)
                        options = Option.objects.filter(id__in=options)
                        survey_answer.options.add(*options)
        except Exception:
            raise ValidationError(
                {
                    "error": _(
                        "Failed to create survey or survey answer due to invalid data"
                    )
                }
            )
        return survey


class Status(graphene.Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"


class HappeningSurveyInput(graphene.InputObjectType):
    category_id = graphene.Int(description="category id", required=True)
    title = graphene.String(description="title", required=True)
    description = graphene.String(description="description", required=False)
    sentiment = graphene.String(description="Sentiment", required=False)
    attachment = graphene.List(Upload, required=False)
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
            for file in data.attachment:
                gallery = Gallery(media=file, title=file.name, type="image")
                gallery.save()
                survey.attachment.add(gallery)
            survey.save()
        return CreateHappeningSurvey(result=survey, ok=True, errors=None)


class UpdateHappeningSurveyInput(graphene.InputObjectType):
    category_id = graphene.Int(description="category id", required=False)
    title = graphene.String(description="title", required=False)
    description = graphene.String(description="description", required=False)
    sentiment = graphene.String(description="Sentiment", required=False)
    attachment = graphene.List(Upload, required=False)
    location = graphql_geojson.Geometry(required=False)
    boundary = graphql_geojson.Geometry(required=False)
    status = Status()


class UpdateHappeningSurvey(graphene.Mutation):
    class Input:
        id = graphene.UUID(description="UUID", required=True)
        data = UpdateHappeningSurveyInput(
            description="Fields required to create a happening survey.",
            required=True,
        )

    errors = GenericScalar()
    ok = graphene.Boolean()
    result = graphene.Field(HappeningSurveyType)

    @login_required
    def mutate(self, info, id, data=None):
        happening_survey_obj = HappeningSurvey.objects.get(id=id)
        for key, value in data.items():
            setattr(happening_survey_obj, key, value)
        try:
            happening_survey_obj.full_clean()
            happening_survey_obj.save()
            return UpdateHappeningSurvey(
                result=happening_survey_obj, errors=None, ok=True
            )
        except ValidationError as e:
            return UpdateHappeningSurvey(result=None, errors=e, ok=False)
