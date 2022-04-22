import graphene
from graphql_jwt.decorators import login_required

from survey.models import (
    LocalEnviromentalSurvey,
    Option,
    ProtectedAreaCategory,
    Question,
    QuestionGroup,
    Survey,
    SurveyAnswer,
)
from survey.mutations import (
    CreateLocalEnviromentalSurvey,
    OptionMutation,
    QuestionGroupMutation,
    QuestionMutation,
    SurveyAnswerMutation,
    SurveyMutation,
)
from survey.types import (
    LocalEnviromentalSurveyType,
    OptionType,
    ProtectedAreaCategoryType,
    QuestionGroupType,
    QuestionType,
    SurveyAnswerType,
    SurveyType,
)


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


class SurveyQueries(graphene.ObjectType):
    option = graphene.List(OptionType, description="Return the options")
    question = graphene.List(QuestionType, description="Return the questions")
    question_group = graphene.List(
        QuestionGroupType, description="Return the question group"
    )
    survey = graphene.List(SurveyType, description="Return the surveys")
    survey_answer = graphene.List(
        SurveyAnswerType, description="Return the survey answer"
    )

    def resolve_question(self, info, **kwargs):
        return Question.objects.all()

    def resolve_question_group(self, info, **kwargs):
        return QuestionGroup.objects.all()

    def resolve_option(self, info, **kwargs):
        return Option.objects.all()

    def resolve_survey(self, info, **kwargs):
        return Survey.objects.all()

    def resolve_survey_answer(self, info, **kwargs):
        return SurveyAnswer.objects.all()


class LocalEnviromentalSurveyMutations(graphene.ObjectType):
    create_enviromental_survey = CreateLocalEnviromentalSurvey.Field()


class SurveyMutations(graphene.ObjectType):
    create_option = OptionMutation.Field()
    create_question_group = QuestionGroupMutation.Field()
    create_question = QuestionMutation.Field()
    create_survey = SurveyMutation.Field()
    create_survey_answer = SurveyAnswerMutation.Field()
