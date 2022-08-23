import graphene
from graphene_django_extras.fields import DjangoFilterPaginateListField

from .filters import OrganizationFilter
from .types import OrganizationType


class OrganizationQueries(graphene.ObjectType):
    organizations = DjangoFilterPaginateListField(
        OrganizationType,
        description="Return organizations",
        filterset_class=OrganizationFilter,
    )
