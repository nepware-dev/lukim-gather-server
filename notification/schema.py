import graphene
from graphene_django_extras import DjangoFilterPaginateListField

from .filters import NotificationFilter
from .types import NotificationType


class NotificationQueries(graphene.ObjectType):
    notifications = DjangoFilterPaginateListField(
        NotificationType,
        description="Return notifications",
        filterset_class=NotificationFilter,
    )
