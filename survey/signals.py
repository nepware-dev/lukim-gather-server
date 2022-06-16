from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from .models import HappeningSurvey


@receiver(post_save, sender=HappeningSurvey)
def send_survey_approval_notification(sender, instance, created, **kwargs):
    update_fields = kwargs.get("update_fields")
    if update_fields and "status" in update_fields:
        if instance.status == "pending":
            return
        instance.created_by.notify(
            instance.updated_by,
            instance.status,
            action_object=instance,
            notification_type=f"happening_survey_{instance.status}",
        )
