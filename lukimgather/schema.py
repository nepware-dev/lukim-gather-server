import graphene
from django.conf import settings
from graphene_django.debug import DjangoDebug

from user.schema import UserMutations, UserQueries


class Query(UserQueries, graphene.ObjectType):
    if settings.DEBUG:
        debug = graphene.Field(DjangoDebug, name="_debug")


class Mutation(UserMutations, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
