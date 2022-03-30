import graphene
from graphql_jwt.decorators import login_required

from survey.models import LocalEnviromentalSurvey, ProtectedAreaCategory
from survey.mutations import CreateLocalEnviromentalSurvey
from survey.types import LocalEnviromentalSurveyType, ProtectedAreaCategoryType


class LocalEnviromentalSurveyQueries(graphene.ObjectType):
    enviromental_surveys = graphene.List(
        LocalEnviromentalSurveyType, description="Return the local enviromental survey"
    )
    protected_area_categories = graphene.List(
        ProtectedAreaCategoryType, description="Return the protected area categories"
    )

    @login_required
    def resolve_enviromental_surveys(self, info, **kwargs):
        return LocalEnviromentalSurvey.objects.all()

    @login_required
    def resolve_enviromental_survey(self, info, enviromental_survey_id):
        return LocalEnviromentalSurvey.objects.get(id=enviromental_survey_id)

    @login_required
    def resolve_protected_area_categories(self, info, level=None, **kwargs):
        return ProtectedAreaCategory.objects.filter(level=0)


class LocalEnviromentalSurveyMutations(graphene.ObjectType):
    create_survey = CreateLocalEnviromentalSurvey.Field()
