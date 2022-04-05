import graphene
import graphql_geojson
from graphene.types.generic import GenericScalar
from graphql_jwt.decorators import login_required

from gallery.models import Gallery
from survey.models import LocalEnviromentalSurvey
from survey.types import LocalEnviromentalSurveyType


class LocalEnviromentalSurveyInput(graphene.InputObjectType):
    category_id = graphene.Int(description="category id", required=True)
    title = graphene.String(description="title", required=True)
    description = graphene.String(description="description", required=False)
    sentiment = graphene.String(description="Sentiment", required=False)
    attachment = graphene.List(graphene.ID, description="attachments", required=False)
    location = graphql_geojson.Geometry(required=False)
    boundary = graphql_geojson.Geometry(required=False)


class CreateLocalEnviromentalSurvey(graphene.Mutation):
    class Arguments:
        data = LocalEnviromentalSurveyInput(
            description="Fields required to create a local enviromental survey.",
            required=True,
        )

    errors = GenericScalar()
    result = graphene.Field(LocalEnviromentalSurveyType)
    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, data):
        survey = LocalEnviromentalSurvey.objects.create(
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
        return CreateLocalEnviromentalSurvey(result=survey, ok=True, errors=None)
