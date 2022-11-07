import graphene
from django.db.models import Count
from graphene_django.types import DjangoObjectType
from graphene_django_extras.paginations import LimitOffsetGraphqlPagination

from project.models import Project

from .models import Organization


class OrganizationType(DjangoObjectType):
    class Meta:
        model = Organization
        description = "Type defincation for a organization"
        paginations = LimitOffsetGraphqlPagination(ordering="title")

    members_count = graphene.Int()

    def resolve_members_count(root, info, **kwargs):
        members_count = Project.objects.filter(organization=root).aggregate(
            members_count=Count("users", distinct=True)
        )
        return members_count.get("members_count")

    def resolve_logo(self, info):
        if self.logo and self.logo.url:
            return info.context.build_absolute_uri(self.logo.url)
        else:
            return None
