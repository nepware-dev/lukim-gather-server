from graphene_django.types import DjangoObjectType
from graphene_django_extras.paginations import LimitOffsetGraphqlPagination

from .models import ProtectedArea, Region


class RegionType(DjangoObjectType):
    class Meta:
        model = Region
        exclude = ("boundary",)
        description = "Type definition for a region"
        pagination = LimitOffsetGraphqlPagination(default_limit=200, ordering="-name")


class ProtectedAreaType(DjangoObjectType):
    class Meta:
        model = ProtectedArea
        exclude = ("boundary",)
        description = "Type definition for a protected area"
        pagination = LimitOffsetGraphqlPagination(default_limit=200, ordering="-name")
