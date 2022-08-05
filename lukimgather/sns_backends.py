import boto3
from django.conf import settings


class SnsBackend:
    def send_messages(self, to, message):
        client = boto3.client(
            "sns",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_SNS_REGION_NAME,
        )
        try:
            client.publish(PhoneNumber=to, Message=message)
        except:
            raise
