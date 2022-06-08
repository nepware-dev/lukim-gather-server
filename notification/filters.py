import django_filters

from .models import Notice, Notification


class NotificationFilter(django_filters.FilterSet):
    class Meta:
        model = Notification
        fields = {
            "has_read": ["exact"],
            "notification_type": ["exact"],
            "actor_content_type__model": ["exact"],
            "timestamp": ["gte", "lte"],
            "target_content_type__model": ["exact"],
            "action_object_content_type__model": ["exact"],
        }

    @property
    def qs(self):
        parent = super(NotificationFilter, self).qs
        if self.request.user.is_anonymous:
            return parent.none()
        return parent.filter(recipient=self.request.user)


class NoticeFilter(django_filters.FilterSet):
    class Meta:
        model = Notice
        fields = {
            "title": ["contains"],
            "description": ["contains"],
            "notice_type": ["exact"],
        }
