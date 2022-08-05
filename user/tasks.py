from celery import shared_task
from django.contrib.auth import get_user_model

from lukimgather.celery import no_simultaneous_execution
from lukimgather.sns_backends import SnsBackend


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=30,
    retry_kwargs={"max_retries": 3},
)
@no_simultaneous_execution
def send_user_mail(self, user_id, subject, message, from_email, **kwargs):
    get_user_model().objects.get(id=user_id).email_user(
        subject, message, from_email=from_email, **kwargs
    )


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=30,
    retry_kwargs={"max_retries": 3},
)
@no_simultaneous_execution
def send_user_sms(self, to, message, **kwargs):
    SnsBackend.send_messages(self, to=to, message=message)
