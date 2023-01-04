import graphene
from graphene.types.generic import GenericScalar
from graphene_django.rest_framework.mutation import ErrorType, get_object_or_404
from graphql_jwt.decorators import login_required, staff_member_required

from project.models import Project, ProjectUser
from user.models import User


class AddProjectUserMutationInput(graphene.InputObjectType):
    id = graphene.ID()
    users = graphene.List(graphene.ID)


class AddProjectUserMutation(graphene.Mutation):
    class Arguments:
        input = AddProjectUserMutationInput(required=True)

    ok = graphene.Boolean()
    errors = graphene.Field(ErrorType)

    @classmethod
    @login_required
    def mutate(cls, root, info, input):
        try:
            users = User.objects.filter(id__in=input.get("users"))
            project = get_object_or_404(Project, id=input.get("id"))
            if users and project:
                for user in users:
                    project.users.add(user.id)
        except Exception as e:
            return cls(ok=False, errors={"field": "id", "messages": {str(e)}})
        return cls(ok=True, errors=None)


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
