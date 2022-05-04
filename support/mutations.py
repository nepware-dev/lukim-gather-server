from graphene_django.rest_framework.mutation import SerializerMutation

from support.serializers import FeedbackSerializer


class FeedbackMutation(SerializerMutation):
    class Meta:
        serializer_class = FeedbackSerializer
