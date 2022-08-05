import graphene
from graphene_django_extras import DjangoFilterPaginateListField

from .filters import ProtectedAreaFilter, RegionFilter
from .types import ProtectedAreaType, RegionType


class RegionQueries(graphene.ObjectType):
    regions = DjangoFilterPaginateListField(
        RegionType, description="Returns regions", filterset_class=RegionFilter
    )
    protected_areas = DjangoFilterPaginateListField(
        ProtectedAreaType,
        description="Returns protected areas",
        filterset_class=ProtectedAreaFilter,
    )
