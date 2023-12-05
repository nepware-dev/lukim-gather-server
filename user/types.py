import graphene
from graphene_django.types import DjangoObjectType

from lukimgather.resolvers import staff_resolver
from user.models import Grant, PasswordResetPin, User


class PrivateUserType(DjangoObjectType):
    has_password = graphene.Boolean(
        description="Determine if user has set password or not."
    )
    has_project_permission = graphene.Boolean(
        description="Determine if user can accept/reject project."
    )

    class Meta:
        model = User
        exclude = ("password",)

    def resolve_avatar(self, info):
        if not self.avatar or not self.avatar.url:
            return None
        return info.context.build_absolute_uri(self.avatar.url)

    def resolve_has_password(self, info):
        if self.has_usable_password():
            return True
        return False

    def resolve_has_project_permission(self, info):
        user_perm = info.context.user.user_permissions.filter(
            codename="can_accept_reject_project"
        ).exists()
        if info.context.user.is_superuser or user_perm:
            return True
        return False


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "avatar")

    def resolve_avatar(self, info):
        if not self.avatar or not self.avatar.url:
            return None
        return info.context.build_absolute_uri(self.avatar.url)


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
