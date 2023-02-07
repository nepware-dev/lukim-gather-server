from enum import Enum

import graphene
import graphql_geojson
import reversion
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from graphene.types.generic import GenericScalar
from graphene_django.rest_framework.mutation import ErrorType, SerializerMutation
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from reversion.models import Version

from gallery.models import Gallery
from lukimgather.utils import is_valid_uuid
from survey.models import HappeningSurvey, Survey
from survey.serializers import SurveySerializer
from survey.types import HappeningSurveyType, SurveyType


class WritableSurveyMutation(SerializerMutation):
    class Meta:
        serializer_class = SurveySerializer
        fields = "__all__"

    @classmethod
    def perform_mutate(cls, serializer, info):
        if not info.context.user.is_anonymous:
            serializer.save(created_by=info.context.user)
        return super().perform_mutate(serializer, info)


class UpdateSurveyMutation(graphene.Mutation):
    class Input:
        id = graphene.ID(description="ID", required=True)
        answer = graphene.JSONString(required=True)

    errors = graphene.Field(ErrorType)
    ok = graphene.Boolean()
    result = graphene.Field(SurveyType)

    @login_required
    def mutate(self, info, id, answer):
        if not isinstance(answer, dict):
            raise GraphQLError("Answer must be a valid JSON object.")
        try:
            survey_obj = Survey.objects.get(id=id)
            survey_obj.answer = answer
            survey_obj.updated_by = info.context.user
            survey_obj.save()
        except Exception as e:
            return UpdateSurveyMutation(
                result=None, ok=False, errors={"field": "id", "messages": {str(e)}}
            )
        return UpdateSurveyMutation(result=survey_obj, ok=True, errors=None)


class Status(graphene.Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"


class Improvement(graphene.Enum):
    INCREASING = "increasing"
    SAME = "same"
    DECREASING = "decreasing"


class HappeningSurveyInput(graphene.InputObjectType):
    id = graphene.UUID(description="uuid", require=False)
    category_id = graphene.Int(description="category id", required=True)
    project_id = graphene.Int(description="project id")
    title = graphene.String(description="title", required=True)
    description = graphene.String(description="description", required=False)
    sentiment = graphene.String(description="Sentiment", required=False)
    attachment = graphene.List(Upload, required=False)
    location = graphql_geojson.Geometry(required=False)
    boundary = graphql_geojson.Geometry(required=False)
    improvement = Improvement(required=False)
    is_public = graphene.Boolean(default=True, required=False)
    is_test = graphene.Boolean(default=False, required=False)
    is_offline = graphene.Boolean(default=False, required=False)
    created_at = graphene.DateTime(required=False)


class CreateHappeningSurvey(graphene.Mutation):
    class Arguments:
        anonymous = graphene.Boolean(default_value=False, required=True)
        data = HappeningSurveyInput(
            description="Fields required to create a happening survey.",
            required=True,
        )

    errors = GenericScalar()
    result = graphene.Field(HappeningSurveyType)
    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, anonymous, data):
        try:
            with transaction.atomic(), reversion.create_revision():
                id = data.get("id", None)
                if id:
                    survey_obj = HappeningSurvey.objects.create(
                        id=id,
                        category_id=data.get("category_id"),
                        project_id=data.get("project_id"),
                    )
                else:
                    survey_obj = HappeningSurvey.objects.create(
                        category_id=data.get("category_id"),
                        project_id=data.get("project_id"),
                    )
                survey_obj.title = data.get("title")
                survey_obj.description = data.get("description")
                survey_obj.sentiment = data.get("sentiment")
                survey_obj.improvement = (
                    None if not data.get("improvement") else data.improvement.value
                )
                survey_obj.location = data.get("location")
                survey_obj.boundary = data.get("boundary")
                survey_obj.is_public = data.get("is_public", True)
                survey_obj.is_test = data.get("is_test", False)
                survey_obj.created_by = None if anonymous else info.context.user
                if "created_at" in data:
                    survey_obj.created_at = data.get("created_at")
                if data.get("attachment"):
                    for file in data.attachment:
                        if is_valid_uuid(file.name):
                            gallery = Gallery(
                                id=file.name,
                                media=file,
                                title=file.name,
                                type="image",
                            )
                        else:
                            gallery = Gallery(
                                media=file,
                                title=file.name,
                                type="image",
                            )
                        gallery.save()
                        survey_obj.attachment.add(gallery)
                survey_obj.save()
                reversion.set_comment("Initial version.")
        except Exception:
            raise GraphQLError("Failed to create happening survey")
        return CreateHappeningSurvey(result=survey_obj, ok=True, errors=None)


class DeleteHappeningSurvey(graphene.Mutation):
    ok = graphene.Boolean()
    errors = GenericScalar()

    class Arguments:
        id = graphene.UUID(description="UUID", required=True)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            happening_survey_obj = HappeningSurvey.objects.get(pk=kwargs["id"])
            happening_survey_obj.delete()
            return cls(ok=True, errors=None)
        except Exception as e:
            return cls(ok=False, errors=e)


class UpdateHappeningSurveyInput(graphene.InputObjectType):
    category_id = graphene.Int(description="category id", required=False)
    project_id = graphene.Int(description="project id", required=False)
    title = graphene.String(description="title", required=False)
    description = graphene.String(description="description", required=False)
    sentiment = graphene.String(description="Sentiment", required=False)
    attachment = graphene.List(Upload, required=False)
    attachment_link = graphene.List(graphene.UUID, required=False)
    location = graphql_geojson.Geometry(required=False)
    boundary = graphql_geojson.Geometry(required=False)
    status = Status()
    improvement = Improvement(required=False)
    is_public = graphene.Boolean(default=True, required=False)
    is_test = graphene.Boolean(default=False, required=False)
    is_offline = graphene.Boolean(default=False, required=False)
    modified_at = graphene.DateTime(required=False)


class UpdateHappeningSurvey(graphene.Mutation):
    class Input:
        id = graphene.UUID(description="UUID", required=True)
        data = UpdateHappeningSurveyInput(
            description="Fields required to update a happening survey.",
            required=True,
        )

    errors = GenericScalar()
    ok = graphene.Boolean()
    result = graphene.Field(HappeningSurveyType)

    @login_required
    def mutate(self, info, id, data=None):
        happening_survey_obj = HappeningSurvey.objects.filter(id=id).first()
        if not happening_survey_obj:
            raise GraphQLError("Happening survey doesn't exist")

        attachment_links = data.pop("attachment_link", None)
        attachments = data.pop("attachment", [])
        for key, value in data.items():
            if isinstance(value, Enum):
                value = value.value
            setattr(happening_survey_obj, key, value)

        try:
            with transaction.atomic(), reversion.create_revision():
                happening_survey_obj.full_clean()
                happening_survey_obj.updated_by = info.context.user
                happening_survey_obj.modified_at = data.get(
                    "modified_at", timezone.now()
                )
                if attachment_links is not None:
                    happening_survey_obj.attachment.set(attachment_links)
                if attachments:
                    for attachment in attachments:
                        new_attachment = happening_survey_obj.attachment.create(
                            media=attachment,
                            title=attachment.name,
                            type="image",
                            id=attachment.name
                            if is_valid_uuid(attachment.name)
                            else None,
                        )
                        happening_survey_obj.attachment.add(new_attachment)
                happening_survey_obj.save()
                version_no = Version.objects.get_for_object(
                    happening_survey_obj
                ).count()
                reversion.set_comment(f"v{version_no}")
        except ValidationError as e:
            return UpdateHappeningSurvey(result=None, errors=e, ok=False)
        except Exception:
            raise GraphQLError("Failed to update happening survey")
        return UpdateHappeningSurvey(result=happening_survey_obj, errors=None, ok=True)


class EditHappeningSurvey(graphene.Mutation):
    class Input:
        id = graphene.UUID(description="UUID", required=True)
        data = UpdateHappeningSurveyInput(
            description="Fields required to edit a happening survey.",
            required=True,
        )

    errors = GenericScalar()
    ok = graphene.Boolean()
    result = graphene.Field(HappeningSurveyType)

    @login_required
    def mutate(self, info, id, data=None):
        happening_survey_obj = HappeningSurvey.objects.filter(id=id).first()
        if not happening_survey_obj:
            raise GraphQLError("Happening survey doesn't exist")

        attachment_links = data.pop("attachment_link", None)
        attachments = data.pop("attachment", [])

        for key, value in data.items():
            if isinstance(value, Enum):
                value = value.value
            setattr(happening_survey_obj, key, value)

        try:
            with transaction.atomic():
                happening_survey_obj.full_clean()
                if attachment_links is not None:
                    happening_survey_obj.attachment.set(attachment_links)
                happening_survey_obj.updated_by = info.context.user
                happening_survey_obj.modified_at = data.get(
                    "modified_at", timezone.now()
                )
                happening_survey_obj.save()
                if attachments:
                    for attachment in attachments:
                        new_attachment = happening_survey_obj.attachment.create(
                            media=attachment,
                            title=attachment.name,
                            type="image",
                            id=attachment.name
                            if is_valid_uuid(attachment.name)
                            else None,
                        )
                        happening_survey_obj.attachment.add(new_attachment)
        except ValidationError as e:
            return EditHappeningSurvey(result=None, errors=e, ok=False)
        except Exception:
            raise GraphQLError("Failed to edit happening survey")
        return EditHappeningSurvey(result=happening_survey_obj, errors=None, ok=True)
