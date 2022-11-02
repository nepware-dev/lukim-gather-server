from celery.utils.imports import instantiate
from django.db.models.signals import m2m_changed, post_save
from django.dispatch.dispatcher import receiver
from django.utils.html import strip_tags

from project.models import Project
from support.models import EmailTemplate
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
            project_users = Project.objects.filter(organization=organization).distinct()
            for user in project_users:
                user.notify(
                    user,
                    instance.title,
                    action_object=instance,
                    notification_type="announcement",
                    description=strip_tags(instance.description),
                )
    elif "notification.Announcement_user" in sender._meta.label or instance.notify_all:
        users = User.objects.all() if instance.notify_all else instance.user.all()
        for user in users:
            user.notify(
                user,
                instance.title,
                action_object=instance,
                notification_type="announcement",
                description=strip_tags(instance.description),
            )
            if not instance.notify_all:
                subject, html_message, text_message = EmailTemplate.objects.get(
                    identifier="announcement"
                ).get_email_contents(
                    {
                        "user": user,
                        "announcement_object": strip_tags(instance.description),
                    }
                )
                if user.phone_number:
                    user.celery_sms_user(
                        to=user.phone_number.as_international, message=text_message
                    )
                elif user.email:
                    user.celery_email_user(
                        subject, text_message, html_message=html_message
                    )
