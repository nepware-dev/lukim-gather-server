from graphene_django.types import DjangoObjectType

from user.models import User


class UserType(DjangoObjectType):
    class Meta:
        model = User
        exclude = ("password",)
