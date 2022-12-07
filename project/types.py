import graphene
from graphene_django.types import DjangoObjectType
from graphene_django_extras.paginations import LimitOffsetGraphqlPagination

from project.models import Project


class ProjectType(DjangoObjectType):
    total_users = graphene.Int()

    class Meta:
        model = Project
        description = "Type defination for a project"
        fields = "__all__"
        pagination = LimitOffsetGraphqlPagination(default_limit=100, ordering="-order")

    def resolve_total_users(self, info):
        return self.users.count()
