import graphene
from graphene.types.generic import GenericScalar
from graphene_django.rest_framework.mutation import (
    SerializerMutation,
    get_object_or_404,
)
from graphql_jwt.decorators import login_required, staff_member_required

from project.models import Project, ProjectUser
from project.serializers import ProjectSerializer
from user.models import User


class AddProjectUserMutation(SerializerMutation):
    class Input:
        users = graphene.List(graphene.ID)

    class Meta:
        serializer_class = ProjectSerializer
        model_operations = ["update"]

    @classmethod
    @login_required
    def get_serializer_kwargs(cls, root, info, **input):
        if "users" and "id" in input:
            users = User.objects.filter(id__in=input.get("users"))
            project = get_object_or_404(Project, id=input.get("id"))
            if users and project:
                for user in users:
                    project.users.add(user.id)
        return {"data": input, "partial": True}


class ProjectUserDeleteMutation(graphene.Mutation):
    class Arguments:
        project_id = graphene.ID(required=True)
        user_id = graphene.ID(required=True)

    ok = graphene.Boolean()
    errors = GenericScalar()

    @classmethod
    @login_required
    @staff_member_required
    def mutate(cls, root, info, project_id, user_id):
        try:
            get_object_or_404(ProjectUser, user=user_id, project=project_id).delete()
        except Exception as e:
            return cls(ok=False, errors=str(e))
        return cls(ok=True, errors=None)
