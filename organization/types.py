import graphene
from graphene_django.types import DjangoObjectType
from graphene_django_extras.paginations import LimitOffsetGraphqlPagination

from .models import Organization


class OrganizationType(DjangoObjectType):
    class Meta:
        model = Organization
        description = "Type defincation for a organization"
        paginations = LimitOffsetGraphqlPagination(ordering="title")
        exclude = ("members",)

    members_count = graphene.Int()

    def resolve_members_count(root, info, **kwargs):
        return root.members.count()

    def resolve_logo(self, info):
        if self.logo and self.logo.url:
            return info.context.build_absolute_uri(self.logo.url)
        else:
            return None
