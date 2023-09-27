from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.utils.html import strip_tags

from .models import ContactUs


@receiver(post_save, sender=ContactUs)
def send_contact_us_email(sender, instance, **kwargs):
    if instance:
        send_mail(
            instance.subject,
            instance.message,
            from_email=instance.email,
            recipient_list=["info@png-nrmhub.org"],
            html_message=strip_tags(instance.message),
        )
