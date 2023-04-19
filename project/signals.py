from django.db.models.signals import post_delete, post_save
from django.dispatch.dispatcher import receiver

from project.models import ProjectUser


@receiver(post_save, sender=ProjectUser)
def send_project_user_add_notification(sender, instance, created, **kwargs):
    if created:
        instance.user.notify(
            instance.user,
            instance.project.title,
            action_object=instance,
            notification_type="project_user_add",
            description=f'You have been added to the project "{instance.project.title}".',
        )
        instance.user.send_push_notification(
            message=f'You have been added to the project "{instance.project.title}".'
        )


@receiver(post_delete, sender=ProjectUser)
def send_project_user_delete_notification(sender, instance, *args, **kwargs):
    instance.user.notify(
        instance.user,
        instance.project.title,
        action_object=instance,
        notification_type="project_user_delete",
        description=f'You have been removed from the project "{instance.project.title}."',
    )
    instance.user.send_push_notification(
        message=f'You have been removed from project "{instance.project.title}"'
    )
