from rest_framework import serializers
from validate_email import validate_email

from lukimgather.serializers import UserModelSerializer
from support.models import AccountDeletionRequest, ContactUs, Feedback


class FeedbackSerializer(UserModelSerializer):
    class Meta:
        model = Feedback
        fields = "__all__"


class AccountDeletionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountDeletionRequest
        fields = ("reason",)


class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = "__all__"

    def validate(self, attrs):
        email = attrs.get("email", None)
        if email:
            if not validate_email(email, check_smtp=False):
                raise serializers.ValidationError("Invalid email address.")
        return super().validate(attrs)
