import graphene
import graphql_jwt
from django.utils.translation import gettext_lazy as _

from user.mutations import (
    ChangePassword,
    EmailChange,
    EmailChangeVerify,
    EmailConfirm,
    EmailConfirmVerify,
    PasswordResetChange,
    RegisterUser,
    ResetUserPassword,
    ResetUserPasswordVerify,
)
from user.types import UserType


class UserQueries(graphene.ObjectType):
    me = graphene.Field(
        UserType, description=_("Return the currently authenticated user.")
    )

    def resolve_me(self, info):
        user = info.context.user
        return user if user.is_authenticated else None


class UserMutations(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    change_password = ChangePassword.Field()
    register_user = RegisterUser.Field()
    password_reset = ResetUserPassword.Field()
    password_reset_verify = ResetUserPasswordVerify.Field()
    password_reset_change = PasswordResetChange.Field()
    email_confirm = EmailConfirm.Field()
    email_confirm_verify = EmailConfirmVerify.Field()
    email_change = EmailChange.Field()
    email_change_verify = EmailChangeVerify.Field()
