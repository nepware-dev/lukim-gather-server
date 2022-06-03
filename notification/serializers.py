from django.contrib.contenttypes.models import ContentType
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
