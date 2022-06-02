from graphene_django.types import DjangoObjectType
from graphene_django_extras.paginations import LimitOffsetGraphqlPagination

from .models import Notification


class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification
        description = "Type definition for a notification"
        pagination = LimitOffsetGraphqlPagination(ordering="-name")
