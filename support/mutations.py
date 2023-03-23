from graphene_django.rest_framework.mutation import ErrorType, SerializerMutation
from rest_framework import serializers

from support.serializers import (
    AccountDeletionRequestSerializer,
    ContactUsSerializer,
    FeedbackSerializer,
)
from user.models import User


class FeedbackMutation(SerializerMutation):
    class Meta:
        serializer_class = FeedbackSerializer


class ContactUsMutation(SerializerMutation):
    class Meta:
        serializer_class = ContactUsSerializer


class AccountDeletionRequestMutation(SerializerMutation):
    class Meta:
        serializer_class = AccountDeletionRequestSerializer
        model_operations = [
            "create",
        ]

    @classmethod
    def perform_mutate(cls, serializer, info):
        user_obj = User.objects.filter(pk=info.context.user.id, is_active=True).first()
        if not user_obj:
            return cls(errors={ErrorType(field="account", messages={"User not found"})})
        else:
            user_obj.is_active = False
            user_obj.save()
            obj = serializer.save(account=info.context.user)
            kwargs = {}
            for f, field in serializer.fields.items():
                if not field.write_only:
                    if isinstance(field, serializers.SerializerMethodField):
                        kwargs[f] = field.to_representation(obj)
                    else:
                        kwargs[f] = field.get_attribute(obj)
            return cls(errors=None, **kwargs)
