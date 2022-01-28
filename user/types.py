from graphene_django.types import DjangoObjectType

from user.models import PasswordResetPin, User


class UserType(DjangoObjectType):
    class Meta:
        model = User
        exclude = ("password",)


class PasswordResetPinType(DjangoObjectType):
    class Meta:
        model = PasswordResetPin
        fields = ("identifier",)
