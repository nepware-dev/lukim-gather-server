import graphene
from graphene_django_extras import DjangoFilterPaginateListField

from .filters import NoticeFilter, NotificationFilter
from .types import NoticeType, NotificationType


class NotificationQueries(graphene.ObjectType):
    notifications = DjangoFilterPaginateListField(
        NotificationType,
        description="Return notifications",
        filterset_class=NotificationFilter,
    )


class NoticeQueries(graphene.ObjectType):
    notice = DjangoFilterPaginateListField(
        NoticeType, description="Return notice", filterset_class=NoticeFilter
    )
