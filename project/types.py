import graphene
from graphene_django.types import DjangoObjectType
from graphene_django_extras.paginations import LimitOffsetGraphqlPagination

from project.models import Project, ProjectUser
from survey.models import HappeningSurvey


class ProjectType(DjangoObjectType):
    total_users = graphene.Int()
    is_admin = graphene.Boolean()
    survey_count = graphene.Int()
    survey_last_modified = graphene.DateTime()

    class Meta:
        model = Project
        description = "Type defination for a project"
        fields = "__all__"
        pagination = LimitOffsetGraphqlPagination(default_limit=100, ordering="-order")

    def resolve_total_users(self, info):
        return self.users.count()

    def resolve_is_admin(self, info):
        is_admin = ProjectUser.objects.filter(
            project=self, user=info.context.user, is_admin=True
        )
        if is_admin:
            return True
        return False

    def resolve_survey_count(self, info):
        return HappeningSurvey.objects.filter(project=self).count()

    def resolve_survey_last_modified(self, info):
        obj = (
            HappeningSurvey.objects.filter(project=self)
            .order_by("-modified_at")
            .first()
        )
        return None if not obj else obj.modified_at
