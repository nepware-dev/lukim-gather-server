import graphene
from django.utils import timezone
from django.utils.translation import gettext as _
from graphene_django_extras import DjangoFilterPaginateListField
from graphql_jwt.decorators import login_required

from .filters import NoticeFilter, NotificationFilter
from .models import Notification
from .mutations import MarkNotification
from .types import NoticeType, NotificationType


class NotificationQueries(graphene.ObjectType):
    notifications = DjangoFilterPaginateListField(
        NotificationType,
        description="Return notifications",
        filterset_class=NotificationFilter,
    )
    notification_unread_count = graphene.Int()

    @login_required
    def resolve_notification_unread_count(root, info):
        return Notification.objects.filter(
            recipient=info.context.user, has_read=False
        ).count()


class NoticeQueries(graphene.ObjectType):
    notice = DjangoFilterPaginateListField(
        NoticeType, description="Return notice", filterset_class=NoticeFilter
    )


class NotificationMutations(graphene.ObjectType):
    mark_as_read = MarkNotification.Field()
