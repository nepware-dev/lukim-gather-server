import graphene
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from graphene_django.rest_framework.mutation import ErrorType, SerializerMutation
from graphql_jwt.decorators import login_required
from push_notifications.models import APNSDevice, GCMDevice
from rest_framework import serializers

from notification.serializers import (
    CustomAPNSDeviceSerializer,
    CustomGCMDeviceSerializer,
)

from .models import Notification


class MarkNotification(graphene.Mutation):
    class Arguments:
        pk = graphene.Int(required=False)
        all = graphene.Boolean(required=False)

    detail = graphene.String()

    @login_required
    def mutate(root, info, pk=None, all=None):
        try:
            notification_obj = Notification.objects.filter(recipient=info.context.user)
            message = None
            if all:
                notification_obj.update(has_read=True, modified_at=timezone.now())
                message = _("Successfully marked all notification as read")
            if pk:
                notification_obj.filter(pk=pk).update(
                    has_read=True, modified_at=timezone.now()
                )
                message = _("Successfully marked as read")
            return MarkNotification(detail=message)
        except Exception as e:
            raise Exception(e)


class GCMDeviceMutation(SerializerMutation):
    class Meta:
        serializer_class = CustomGCMDeviceSerializer
        fields = "__all__"

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        kwargs = cls.get_serializer_kwargs(root, info, **input)
        serializer = cls._meta.serializer_class(**kwargs)

        if settings.PUSH_NOTIFICATIONS_SETTINGS.get("UPDATE_ON_DUPLICATE_REG_ID"):
            registration_id = serializer.initial_data.get("registration_id")
            instance = GCMDevice.objects.filter(registration_id=registration_id).first()
            if instance:
                return cls.perform_partial_mutate(instance, serializer, info)
        if serializer.is_valid():
            return cls.perform_mutate(serializer, info)
        else:
            errors = ErrorType.from_errors(serializer.errors)
            return cls(errors=errors)

    @classmethod
    def perform_partial_mutate(cls, instance, serializer, info):
        initial_data = serializer.initial_data
        cloud_message_type = initial_data.get("cloud_message_type")
        if cloud_message_type:
            initial_data["cloud_message_type"] = cloud_message_type.value
        if not info.context.user.is_anonymous:
            initial_data["user"] = info.context.user
        obj = serializer.update(instance, initial_data)
        kwargs = {}
        for f, field in serializer.fields.items():
            if not field.write_only:
                if isinstance(field, serializers.SerializerMethodField):
                    kwargs[f] = field.to_representation(obj)
                else:
                    kwargs[f] = field.get_attribute(obj)

        return cls(errors=None, **kwargs)

    @classmethod
    def perform_mutate(cls, serializer, info):
        cloud_message_type = serializer.validated_data.get("cloud_message_type")
        cloud_message_type = (
            "FCM" if not cloud_message_type else cloud_message_type.value
        )
        if not info.context.user.is_anonymous:
            serializer.save(
                user=info.context.user, cloud_message_type=cloud_message_type
            )
        return super().perform_mutate(serializer, info)


class APNSDeviceMutation(SerializerMutation):
    class Meta:
        serializer_class = CustomAPNSDeviceSerializer
        fields = "__all__"

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        kwargs = cls.get_serializer_kwargs(root, info, **input)
        serializer = cls._meta.serializer_class(**kwargs)

        if settings.PUSH_NOTIFICATIONS_SETTINGS.get("UPDATE_ON_DUPLICATE_REG_ID"):
            registration_id = serializer.initial_data.get("registration_id")
            instance = APNSDevice.objects.filter(
                registration_id=registration_id
            ).first()
            if instance:
                return cls.perform_partial_mutate(instance, serializer, info)
        if serializer.is_valid():
            return cls.perform_mutate(serializer, info)
        else:
            errors = ErrorType.from_errors(serializer.errors)
            return cls(errors=errors)

    @classmethod
    def perform_partial_mutate(cls, instance, serializer, info):
        validated_data = serializer.initial_data
        if not info.context.user.is_anonymous:
            validated_data["user"] = info.context.user
        obj = serializer.update(instance, validated_data)
        kwargs = {}
        for f, field in serializer.fields.items():
            if not field.write_only:
                if isinstance(field, serializers.SerializerMethodField):
                    kwargs[f] = field.to_representation(obj)
                else:
                    kwargs[f] = field.get_attribute(obj)

        return cls(errors=None, **kwargs)

    @classmethod
    def perform_mutate(cls, serializer, info):
        if not info.context.user.is_anonymous:
            serializer.save(user=info.context.user)
        return super().perform_mutate(serializer, info)
