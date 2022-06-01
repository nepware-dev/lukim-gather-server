import graphene
import graphql_geojson
from django.core.exceptions import ValidationError
from django.db import transaction
from graphene.types.generic import GenericScalar
from graphene_django.rest_framework.mutation import SerializerMutation
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from gallery.models import Gallery
from region.models import Region
from survey.models import HappeningSurvey
from survey.serializers import SurveySerializer
from survey.types import HappeningSurveyType


class WritableSurveyMutation(SerializerMutation):
    class Meta:
        serializer_class = SurveySerializer
        fields = "__all__"


class Status(graphene.Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"


class Improvement(graphene.Enum):
    INCREASING = "increasing"
    SAME = "same"
    DECREASING = "decreasing"


class HappeningSurveyInput(graphene.InputObjectType):
    category_id = graphene.Int(description="category id", required=True)
    title = graphene.String(description="title", required=True)
    description = graphene.String(description="description", required=False)
    sentiment = graphene.String(description="Sentiment", required=False)
    attachment = graphene.List(Upload, required=False)
    location = graphql_geojson.Geometry(required=False)
    boundary = graphql_geojson.Geometry(required=False)
    improvement = Improvement(required=False)
    is_public = graphene.Boolean(default=True)


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
            with transaction.atomic():
                region_geo = data.location if data.location else data.boundary
                survey_region = (
                    Region.objects.filter(boundary__bbcontains=region_geo).first()
                    if region_geo
                    else None
                )
                survey = HappeningSurvey.objects.create(
                    category_id=data.category_id,
                    title=data.title,
                    description=data.description,
                    sentiment=data.sentiment,
                    improvement=None
                    if not data.improvement
                    else data.improvement.value,
                    location=data.location,
                    boundary=data.boundary,
                    region=survey_region,
                    is_public=data.get("is_public", True),
                    created_by=None if anonymous else info.context.user,
                )
                if data.attachment:
                    for file in data.attachment:
                        gallery = Gallery(
                            media=file,
                            title=file.name,
                            type="image",
                        )
                        gallery.save()
                        survey.attachment.add(gallery)
                survey.save()
        except Exception:
            raise GraphQLError("Failed to create happening survey")
        return CreateHappeningSurvey(result=survey, ok=True, errors=None)


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
    title = graphene.String(description="title", required=False)
    description = graphene.String(description="description", required=False)
    sentiment = graphene.String(description="Sentiment", required=False)
    attachment = graphene.List(Upload, required=False)
    attachment_link = graphene.List(graphene.Int, required=False)
    location = graphql_geojson.Geometry(required=False)
    boundary = graphql_geojson.Geometry(required=False)
    status = Status()
    improvement = Improvement(required=False)


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
        try:
            with transaction.atomic():
                attachment_links = data.pop("attachment_link", None)
                attachments = data.pop("attachment", [])
                region_geo = data.location if data.location else data.boundary
                happening_survey_obj = HappeningSurvey.objects.get(id=id)
                survey_region = (
                    Region.objects.filter(boundary__bbcontains=region_geo).first()
                    if region_geo
                    else None
                )
                for key, value in data.items():
                    try:
                        value = value.value
                    except AttributeError:
                        pass
                    setattr(happening_survey_obj, key, value)
                try:
                    happening_survey_obj.full_clean()
                    if attachment_links is not None:
                        happening_survey_obj.attachment.set(attachment_links)
                    if happening_survey_obj.region != survey_region:
                        happening_survey_obj.region = survey_region
                    happening_survey_obj.updated_by = info.context.user
                    happening_survey_obj.save()
                    if attachments:
                        for attachment in attachments:
                            new_attachment = happening_survey_obj.attachment.create(
                                media=attachment,
                                title=attachment.name,
                                type="image",
                            )
                            happening_survey_obj.attachment.add(new_attachment)
                except ValidationError as e:
                    return UpdateHappeningSurvey(result=None, errors=e, ok=False)
        except Exception:
            raise GraphQLError("Failed to update happening survey")
        return UpdateHappeningSurvey(result=happening_survey_obj, errors=None, ok=True)
