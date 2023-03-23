from graphql import GraphQLError
from graphql_jwt.compat import GraphQLResolveInfo

from project.models import ProjectUser
from survey.models import HappeningSurvey, Survey


def can_edit_happening_survey(resolver_func):
    def wrap(*args, **kwargs):
        info = next(arg for arg in args if isinstance(arg, GraphQLResolveInfo))
        if not info.context.user.is_authenticated:
            return GraphQLError("You are not logged in!")
        obj = HappeningSurvey.objects.filter(id=kwargs.get("id")).first()
        if not obj:
            raise GraphQLError("Happening survey doesn't exist.")
        is_project_admin = ProjectUser.objects.filter(
            user=info.context.user, is_admin=True, project=obj.project
        ).exists()
        if (
            is_project_admin
            or info.context.user.is_staff
            or info.context.user == obj.created_by
        ):
            return resolver_func(*args, **kwargs)
        raise GraphQLError("You do not have permission to perform this action.")

    return wrap


def can_edit_survey(resolver_func):
    def wrap(*args, **kwargs):
        info = next(arg for arg in args if isinstance(arg, GraphQLResolveInfo))
        if not info.context.user.is_authenticated:
            return GraphQLError("You are not logged in!")
        obj = Survey.objects.filter(id=kwargs.get("id")).first()
        if not obj:
            return GraphQLError("Survey doesn't exist.")
        if info.context.user.is_staff or info.context.user == obj.created_by:
            return resolver_func(*args, **kwargs)
        raise GraphQLError("You do not have permission to perform this action.")

    return wrap
