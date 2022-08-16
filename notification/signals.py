from celery.utils.imports import instantiate
from django.db.models.signals import m2m_changed, post_save
from django.dispatch.dispatcher import receiver

from user.models import User

from .models import Announcement


@receiver(m2m_changed, sender=Announcement.organization.through)
@receiver(m2m_changed, sender=Announcement.user.through)
@receiver(post_save, sender=Announcement)
def send_announcement(sender, instance, **kwargs):
    users = []
    if "notification.Announcement_organization" in sender._meta.label:
        organizations = instance.organization.all()
        for organization in organizations:
            members = organization.members.all()
            for user in members:
                user.notify(
                    user,
                    instance.description,
                    action_object=instance,
                    notification_type="announcement",
                    description=instance.description,
                )
    elif "notification.Announcement_user" in sender._meta.label or instance.notify_all:
        users = User.objects.all() if instance.notify_all else instance.user.all()
        for user in users:
            user.notify(
                user,
                instance.description,
                action_object=instance,
                notification_type="announcement",
                description=instance.description,
            )
