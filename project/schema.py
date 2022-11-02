import graphene
from graphene_django_extras import DjangoFilterPaginateListField

from project.filters import ProjectFilter
from project.types import ProjectType


class ProjectQueries(graphene.ObjectType):
    projects = DjangoFilterPaginateListField(
        ProjectType, description="Returns projects", filterset_class=ProjectFilter
    )
