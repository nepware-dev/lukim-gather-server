from django.contrib.contenttypes.models import ContentType
from push_notifications.api.rest_framework import (
    APNSDeviceSerializer,
    GCMDeviceSerializer,
)
from rest_framework import serializers

from lukimgather.serializers import UserModelSerializer

from .models import Notification


class NotificationSerializer(UserModelSerializer):
    actor_content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.all(),
        slug_field="model",
    )
    target_content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.all(),
        slug_field="model",
    )
    action_object_content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.all(),
        slug_field="model",
    )
    actor_str = serializers.SerializerMethodField()
    target_str = serializers.SerializerMethodField()
    action_object_str = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = "__all__"

    def get_actor_str(self, instance):
        if instance.actor:
            return str(instance.actor)
        else:
            None

    def get_target_str(self, instance):
        if instance.target:
            return str(instance.target)
        else:
            None

    def get_action_object_str(self, instance):
        if instance.action_object:
            return str(instance.action_object)
        else:
            None


class UnReadCountResponseSerializer(serializers.Serializer):
    unread_count = serializers.IntegerField()


class CustomGCMDeviceSerializer(GCMDeviceSerializer):
    device_id = serializers.CharField(
        help_text="ANDROID_ID / TelephonyManager.getDeviceId() (e.g: 0x01)",
        style={"input_type": "text"},
        required=False,
        allow_null=True,
    )

    def validate_device_id(self, value):
        try:
            value = int(value, 16) if type(value) != int else value
        except ValueError:
            raise serializers.ValidationError("Device ID is not a valid hex number")
        return value


class CustomAPNSDeviceSerializer(APNSDeviceSerializer):
    device_id = serializers.CharField(
        help_text="ANDROID_ID / TelephonyManager.getDeviceId() (e.g: 0x01)",
        style={"input_type": "text"},
        required=False,
        allow_null=True,
    )

    def validate_device_id(self, value):
        try:
            value = int(value, 16) if type(value) != int else value
        except ValueError:
            raise serializers.ValidationError("Device ID is not a valid hex number")
        return value
