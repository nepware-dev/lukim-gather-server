import graphene
from graphql_jwt.decorators import login_required

from survey.models import LocalEnviromentalSurvey
from survey.mutations import CreateLocalEnviromentalSurvey
from survey.types import LocalEnviromentalSurveyType


class LocalEnviromentalSurveyQueries(graphene.ObjectType):
    enviromental_surveys = graphene.List(
        LocalEnviromentalSurveyType, description="Return the local enviromental survey"
    )

    @login_required
    def resolve_enviromental_surveys(self, info, **kwargs):
        return LocalEnviromentalSurvey.objects.all()

    @login_required
    def resolve_enviromental_survey(self, info, enviromental_survey_id):
        return LocalEnviromentalSurvey.objects.get(id=enviromental_survey_id)


class LocalEnviromentalSurveyMutations(graphene.ObjectType):
    create_survey = CreateLocalEnviromentalSurvey.Field()
