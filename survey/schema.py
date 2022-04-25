import graphene
from graphql_jwt.decorators import login_required

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
from survey.mutations import (
    CreateHappeningSurvey,
    OptionMutation,
    QuestionGroupMutation,
    QuestionMutation,
    SurveyAnswerMutation,
    SurveyMutation,
    WritableSurveyAnswerMutation,
)
from survey.types import (
    FormType,
    HappeningSurveyType,
    OptionType,
    ProtectedAreaCategoryType,
    QuestionGroupType,
    QuestionType,
    SurveyAnswerType,
    SurveyType,
)


class SurveyQueries(graphene.ObjectType):
    happening_surveys = graphene.List(
        HappeningSurveyType, description="Return the happening survey"
    )
    option = graphene.List(OptionType, description="Return the options")
    protected_area_categories = graphene.List(
        ProtectedAreaCategoryType, description="Return the protected area categories"
    )
    question = graphene.List(QuestionType, description="Return the questions")
    question_group = graphene.List(
        QuestionGroupType, description="Return the question group"
    )
    survey = graphene.List(SurveyType, description="Return the surveys")
    survey_form = graphene.List(FormType, description="Return the survey form")
    survey_answer = graphene.List(
        SurveyAnswerType, description="Return the survey answer"
    )

    def resolve_happening_surveys(self, info, **kwargs):
        return HappeningSurvey.objects.all()

    def resolve_happening_survey(self, info, happening_survey_id):
        return HappeningSurvey.objects.get(id=happening_survey_id)

    def resolve_protected_area_categories(self, info, level=None, **kwargs):
        return ProtectedAreaCategory.objects.filter(level=0)

    def resolve_question(self, info, **kwargs):
        return Question.objects.all()

    def resolve_question_group(self, info, **kwargs):
        return QuestionGroup.objects.all()

    def resolve_option(self, info, **kwargs):
        return Option.objects.all()

    def resolve_survey(self, info, **kwargs):
        return Survey.objects.all()

    def resolve_survey_form(self, info, **kwargs):
        return Form.objects.all()

    def resolve_survey_answer(self, info, **kwargs):
        return SurveyAnswer.objects.all()


class SurveyMutations(graphene.ObjectType):
    create_happening_survey = CreateHappeningSurvey.Field()
    create_option = OptionMutation.Field()
    create_question_group = QuestionGroupMutation.Field()
    create_question = QuestionMutation.Field()
    create_survey = SurveyMutation.Field()
    create_survey_answer = SurveyAnswerMutation.Field()
    create_writable_survey_answer = WritableSurveyAnswerMutation.Field()
