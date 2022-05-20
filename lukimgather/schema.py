import graphene
from django.conf import settings
from graphene_django.debug import DjangoDebug

from gallery.schema import UploadFileMutation
from region.schema import RegionQueries
from support.schema import SupportMutations, SupportQueries
from survey.schema import SurveyMutations, SurveyQueries
from user.schema import UserMutations, UserQueries


class Query(
    UserQueries, SupportQueries, SurveyQueries, RegionQueries, graphene.ObjectType
):
    if settings.DEBUG:
        debug = graphene.Field(DjangoDebug, name="_debug")


class Mutation(
    SurveyMutations,
    SupportMutations,
    UserMutations,
    UploadFileMutation,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
