import graphene
import graphql_jwt
from django.utils.translation import gettext_lazy as _
from graphql_jwt.decorators import login_required

from user.mutations import (
    ChangePassword,
    CustomObtainJSONWebToken,
    EmailChange,
    EmailChangeVerify,
    EmailConfirm,
    EmailConfirmVerify,
    PasswordResetChange,
    RegisterUser,
    ResetUserPassword,
    ResetUserPasswordVerify,
    UpdateUser,
)
from user.types import UserType


class UserQueries(graphene.ObjectType):
    me = graphene.Field(
        UserType, description=_("Return the currently authenticated user.")
    )

    @login_required
    def resolve_me(self, info):
        user = info.context.user
        return user if user.is_authenticated else None


class UserMutations(graphene.ObjectType):
    token_auth = CustomObtainJSONWebToken.Field()
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
    update_user = UpdateUser.Field()
