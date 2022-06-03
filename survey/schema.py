import graphene
from django.db.models import Q
from graphene_django_extras import DjangoFilterPaginateListField

from survey.filters import HappeningSurveyFilter, SurveyFilter
from survey.models import HappeningSurvey
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

    @staticmethod
    def resolve_happening_surveys(root, info, **kwargs):
        if info.context.user.is_staff:
            return HappeningSurvey.objects.all()
        if info.context.user.is_authenticated:
            return HappeningSurvey.objects.exclude(
                ~Q(created_by=info.context.user), is_public=False
            )
        return HappeningSurvey.objects.filter(is_public=True)


class SurveyMutations(graphene.ObjectType):
    create_happening_survey = CreateHappeningSurvey.Field()
    delete_happening_survey = DeleteHappeningSurvey.Field()
    update_happening_survey = UpdateHappeningSurvey.Field()
    create_writable_survey = WritableSurveyMutation.Field()
