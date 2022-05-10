import graphene
from graphene_django_extras import DjangoFilterPaginateListField

from survey.filters import HappeningSurveyFilter, SurveyFilter
from survey.mutations import (
    CreateHappeningSurvey,
    DeleteHappeningSurvey,
    UpdateHappeningSurvey,
    WritableSurveyMutation,
)
from survey.types import (
    FormType,
    HappeningSurveyType,
    ProtectedAreaCategoryType,
    SurveyType,
)


class SurveyQueries(graphene.ObjectType):
    happening_surveys = DjangoFilterPaginateListField(
        HappeningSurveyType,
        description="Return the happening survey",
        filterset_class=HappeningSurveyFilter,
    )
    protected_area_categories = DjangoFilterPaginateListField(
        ProtectedAreaCategoryType, description="Return all protected area category"
    )
    survey = DjangoFilterPaginateListField(
        SurveyType,
        description="Return the surveys",
        filterset_class=SurveyFilter,
    )
    survey_form = DjangoFilterPaginateListField(
        FormType, description="Return the survey form"
    )


class SurveyMutations(graphene.ObjectType):
    create_happening_survey = CreateHappeningSurvey.Field()
    delete_happening_survey = DeleteHappeningSurvey.Field()
    update_happening_survey = UpdateHappeningSurvey.Field()
    create_writable_survey = WritableSurveyMutation.Field()
