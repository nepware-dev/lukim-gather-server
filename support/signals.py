from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from .models import ContactUs, EmailTemplate


@receiver(post_save, sender=ContactUs)
def send_contact_us_email(sender, instance, **kwargs):
    if instance:
        subject, html_message, text_message = EmailTemplate.objects.get(
            identifier="contact_us"
        ).get_email_contents({"contact_us_object": instance})
        send_mail(
            subject,
            instance.message,
            from_email=settings.SERVER_EMAIL,
            recipient_list=["info@png-nrmhub.org"],
            html_message=html_message,
        )
