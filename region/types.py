from graphene_django.types import DjangoObjectType
from graphene_django_extras.paginations import LimitOffsetGraphqlPagination

from .models import Region


class RegionType(DjangoObjectType):
    class Meta:
        model = Region
        exclude = ("boundary",)
        description = "Type definition for a region"
        pagination = LimitOffsetGraphqlPagination(default_limit=200, ordering="-name")
