import graphene
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from graphql_jwt.decorators import login_required

from .models import Notification


class MarkNotification(graphene.Mutation):
    class Arguments:
        pk = graphene.Int(required=False)
        all = graphene.Boolean(required=False)

    detail = graphene.String()

    @login_required
    def mutate(root, info, pk=None, all=None):
        try:
            notification_obj = Notification.objects.filter(recipient=info.context.user)
            message = None
            if all:
                notification_obj.update(has_read=True, modified_at=timezone.now())
                message = _("Successfully marked all notification as read")
            if pk:
                notification_obj.filter(pk=pk).update(
                    has_read=True, modified_at=timezone.now()
                )
                message = _("Successfully marked as read")
            return MarkNotification(detail=message)
        except Exception as e:
            raise Exception(e)
