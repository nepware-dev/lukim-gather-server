from graphene_django.types import DjangoObjectType
from graphene_django_extras.paginations import LimitOffsetGraphqlPagination

from .models import Notice, Notification


class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification
        description = "Type definition for a notification"
        pagination = LimitOffsetGraphqlPagination(ordering="-name")


class NoticeType(DjangoObjectType):
    class Meta:
        model = Notice
        description = "Type definition for a notice"
        pagination = LimitOffsetGraphqlPagination(ordering="-created_at")
