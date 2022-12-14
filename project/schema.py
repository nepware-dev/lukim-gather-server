import graphene
from graphene_django_extras import DjangoFilterPaginateListField

from project.filters import ProjectFilter
from project.mutations import AddProjectUserMutation, ProjectUserDeleteMutation
from project.types import ProjectType


class ProjectQueries(graphene.ObjectType):
    projects = DjangoFilterPaginateListField(
        ProjectType, description="Returns projects", filterset_class=ProjectFilter
    )


class ProjectMutation(graphene.ObjectType):
    add_project_user = AddProjectUserMutation.Field()
    delete_project_user = ProjectUserDeleteMutation.Field()
