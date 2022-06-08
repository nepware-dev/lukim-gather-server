import graphene
from django.conf import settings
from graphene_django.debug import DjangoDebug

from gallery.schema import UploadFileMutation
from notification.schema import NoticeQueries, NotificationQueries
from region.schema import RegionQueries
from support.schema import SupportMutations, SupportQueries
from survey.schema import SurveyMutations, SurveyQueries
from user.schema import UserMutations, UserQueries


class Query(
    NotificationQueries,
    NoticeQueries,
    SupportQueries,
    SurveyQueries,
    RegionQueries,
    UserQueries,
    graphene.ObjectType,
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
