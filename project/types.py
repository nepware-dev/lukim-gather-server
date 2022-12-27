import graphene
from graphene_django.types import DjangoObjectType
from graphene_django_extras.paginations import LimitOffsetGraphqlPagination

from project.models import Project, ProjectUser


class ProjectType(DjangoObjectType):
    total_users = graphene.Int()
    is_admin = graphene.Boolean()

    class Meta:
        model = Project
        description = "Type defination for a project"
        fields = "__all__"
        pagination = LimitOffsetGraphqlPagination(default_limit=100, ordering="-order")

    def resolve_total_users(self, info):
        return self.users.count()

    def resolve_is_admin(self, info):
        is_admin = ProjectUser.objects.filter(
            project=self, user=info.context.user, is_admin=True
        )
        if is_admin:
            return True
        return False
