from rest_framework import serializers

from lukimgather.serializers import UserModelSerializer
from support.models import AccountDeletionRequest, Feedback


class FeedbackSerializer(UserModelSerializer):
    class Meta:
        model = Feedback
        fields = "__all__"


class AccountDeletionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountDeletionRequest
        fields = ("reason",)
