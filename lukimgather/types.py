from graphene_django.types import DjangoObjectType
from reversion.models import Revision


class RevisionType(DjangoObjectType):
    class Meta:
        model = Revision
        description = "Type definition for a revision"
        fields = "__all__"
