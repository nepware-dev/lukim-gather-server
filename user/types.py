import graphene
from graphene_django.types import DjangoObjectType

from lukimgather.resolvers import staff_resolver
from user.models import Grant, PasswordResetPin, User


class PrivateUserType(DjangoObjectType):
    class Meta:
        model = User
        exclude = ("password",)

    def resolve_avatar(self, info):
        if self.avatar and self.avatar.url:
            return info.context.build_absolute_uri(self.avatar.url)
        else:
            return None


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name")


class PasswordResetPinType(DjangoObjectType):
    class Meta:
        model = PasswordResetPin
        fields = ("identifier",)


class GrantType(DjangoObjectType):
    user = graphene.Field(PrivateUserType)

    class Meta:
        model = Grant
        fields = "__all__"
        default_resolver = staff_resolver
