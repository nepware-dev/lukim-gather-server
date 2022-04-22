import graphene
from django.conf import settings
from graphene_django.debug import DjangoDebug

from gallery.schema import UploadFileMutation
from survey.schema import SurveyMutations, SurveyQueries
from user.schema import UserMutations, UserQueries


class Query(UserQueries, SurveyQueries, graphene.ObjectType):
    if settings.DEBUG:
        debug = graphene.Field(DjangoDebug, name="_debug")


class Mutation(
    SurveyMutations,
    UserMutations,
    UploadFileMutation,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
