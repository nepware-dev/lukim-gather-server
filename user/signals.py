from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.template.loader import get_template
from django.utils import timezone

from lukimgather.utils import gen_random_number
from support.models import EmailTemplate

from .models import EmailConfirmationPin, PhoneNumberConfirmationPin


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def send_confiramtion_pin(sender, instance, created, **kwargs):
    if created:
        six_digit_pin = gen_random_number(6)
        active_for_one_hour = timezone.now() + timezone.timedelta(hours=1)
        if instance.email:
            email_confirm_object, _ = EmailConfirmationPin.objects.update_or_create(
                user=instance,
                defaults={
                    "pin": six_digit_pin,
                    "pin_expiry_time": active_for_one_hour,
                    "is_active": True,
                },
            )
            subject, html_message, text_message = EmailTemplate.objects.get(
                identifier="email_confirm"
            ).get_email_contents(
                {"user": instance, "email_confirm_object": email_confirm_object}
            )
            # instance.celery_email_user(subject, text_message, html_message=html_message) # Note:- skip email verification
        if instance.phone_number:
            PhoneNumberConfirmationPin.objects.update_or_create(
                user=instance,
                defaults={
                    "pin": six_digit_pin,
                    "pin_expiry_time": active_for_one_hour,
                    "is_active": True,
                },
            )
            instance.celery_sms_user(
                to=instance.username,
                message=f"Your OTP is {six_digit_pin} for Lukim Gather, It will expire in next 60 minutes.",
            )
