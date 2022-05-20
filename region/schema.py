import graphene
from graphene_django_extras import DjangoFilterPaginateListField

from .filters import RegionFilter
from .types import RegionType


class RegionQueries(graphene.ObjectType):
    regions = DjangoFilterPaginateListField(
        RegionType, description="Returns regions", filterset_class=RegionFilter
    )
