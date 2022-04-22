import graphene
import graphql_jwt
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.template.loader import get_template
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from graphene.types.generic import GenericScalar
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import login_required

from lukimgather.utils import gen_random_number, gen_random_string
from user.models import EmailChangePin, EmailConfirmationPin, PasswordResetPin, User
from user.types import PasswordResetPinType, UserType


class CustomObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user)


class UserInput(graphene.InputObjectType):
    organization = graphene.String(description=_("Organization"), required=False)
    avatar = Upload(required=False)


class RegisterUserInput(graphene.InputObjectType):
    first_name = graphene.String(description=_("First Name"), required=True)
    last_name = graphene.String(description=_("Last Name"), required=True)
    email = graphene.String(description=_("Email"), required=True)
    password = graphene.String(description=_("Password"), required=True)
    re_password = graphene.String(description=_("Retype Password"), required=True)
    username = graphene.String(description=_("Username"), required=True)


class ChangePasswordInput(graphene.InputObjectType):
    password = graphene.String(description=_("Password"), required=True)
    new_password = graphene.String(description=_("New Password"), required=True)
    re_password = graphene.String(description=_("Retype Password"), required=True)


class PasswordResetPinInput(graphene.InputObjectType):
    username = graphene.String(description=_("Username"), required=True)
    no_of_incorrect_attempts = graphene.Int(
        description=_("No Of Incorrect Attempts"), default_value=0
    )
    pin = graphene.Int(description=_("Pin"))
    pin_expiry_time = graphene.DateTime(description=_("Pin Expiry Time"))
    is_active = graphene.Boolean(description=_("Is Active"))
    identifier = graphene.String(description=_("Identifier"))


class PasswordResetChangeInput(graphene.InputObjectType):
    username = graphene.String(description=_("Username"), required=True)
    password = graphene.String(description=_("Password"), required=True)
    re_password = graphene.String(description=_("Retype Password"), required=True)
    identifier = graphene.String(description=_("Identifier"))


class EmailConfirmInput(graphene.InputObjectType):
    username = graphene.String(description=_("Username"), required=True)
    no_of_incorrect_attempts = graphene.Int(
        description=_("No Of Incorrect Attempts"), default_value=0
    )
    pin = graphene.Int(description=_("Pin"))
    pin_expiry_time = graphene.DateTime(description=_("Pin Expiry Time"))
    is_active = graphene.Boolean(description=_("Is Active"))


class EmailChangePinInput(graphene.InputObjectType):
    username = graphene.String(description=_("Username"), required=True)
    no_of_incorrect_attempts = graphene.Int(
        description=_("No Of Incorrect Attempts"), default_value=0
    )
    pin = graphene.Int(description=_("Pin"))
    new_email = graphene.String(description=_("New Email"))
    is_active = graphene.Boolean(description=_("Is Active"))


class EmailChangeInput(graphene.InputObjectType):
    new_email = graphene.String(description=_("New Email"))
    password = graphene.String(description=_("Password"), required=True)


class EmailChangePinVerifyInput(graphene.InputObjectType):
    pin = graphene.Int(description=_("Pin"))


class RegisterUser(graphene.Mutation):
    class Arguments:
        data = RegisterUserInput(
            description=_("Fields required to create a user."), required=True
        )

    errors = GenericScalar()
    result = graphene.Field(UserType)
    ok = graphene.Boolean()

    def mutate(self, info, data):
        user_exists = User.objects.filter_by_username(data.username).exists()
        if user_exists:
            return RegisterUser(
                errors={"error": "User with username/email already exists"},
                ok=False,
            )
        user_password = data.pop("re_password")
        try:
            validate_password(password=user_password)
        except ValidationError as e:
            errors = list(e.messages)
            return RegisterUser(errors={"errors": errors}, ok=False)
        user = User.objects.create_user(**data)
        return RegisterUser(result=user, ok=True, errors=None)


class ChangePassword(graphene.Mutation):
    class Arguments:
        data = ChangePasswordInput(
            description=_("Fields required to change password."), required=True
        )

    errors = GenericScalar()
    ok = graphene.Boolean()
    result = GenericScalar()

    def mutate(self, info, data):
        user = User.objects.filter_by_username(
            info.context.user.username, is_active=True
        ).first()
        new_password = data.new_password
        re_new_password = data.re_password
        if re_new_password != new_password:
            return ChangePassword(
                errors={"error": "New password and re new password doesn't match"},
                result=None,
                ok=False,
            )
        user.set_password(new_password)
        user.save()
        return ChangePassword(
            result={"detail": "Password successfully updated"},
            ok=True,
            errors=None,
        )


class UpdateUser(graphene.Mutation):
    class Arguments:
        data = UserInput(required=True)

    errors = GenericScalar()
    ok = graphene.Boolean()
    result = graphene.Field(UserType)

    @login_required
    def mutate(self, info, data=None):
        user = info.context.user
        for key, value in data.items():
            setattr(user, key, value)
        try:
            user.full_clean()
            user.save()
            return UpdateUser(result=user, errors=None, ok=True)
        except ValidationError as e:
            return UpdateUser(result=user, errors=e, ok=False)


class ResetUserPassword(graphene.Mutation):
    class Arguments:
        data = PasswordResetPinInput(
            description=_("Fields required to reset password."), required=True
        )

    errors = GenericScalar()
    ok = graphene.Boolean()
    result = GenericScalar()

    def mutate(self, info, data):
        username = data.username
        user = User.objects.filter_by_username(username, is_active=True).first()
        if not user:
            return ResetUserPassword(
                errors={
                    "error": "No active user present for username/email your account may be blocked"
                },
                result=None,
                ok=False,
            )
        random_6_digit_pin = gen_random_number(6)
        active_for_one_hour = timezone.now() + timezone.timedelta(hours=1)
        identifier = gen_random_string(length=16)
        password_reset_pin_object, _obj = PasswordResetPin.objects.update_or_create(
            user=user,
            defaults={
                "pin": random_6_digit_pin,
                "pin_expiry_time": active_for_one_hour,
                "is_active": True,
                "identifier": identifier,
            },
        )
        template = get_template("mail/password_reset.txt")
        message = template.render(
            {"user": user, "password_reset_object": password_reset_pin_object}
        )
        user.email_user("Password reset pin", message)
        return ResetUserPassword(
            result={"detail": "Password reset email successfully send"},
            errors=None,
            ok=True,
        )


class ResetUserPasswordVerify(graphene.Mutation):
    class Arguments:
        data = PasswordResetPinInput(
            description=_("Fields required to reset password."), required=True
        )

    errors = GenericScalar()
    ok = graphene.Boolean()
    result = graphene.Field(PasswordResetPinType)

    def mutate(self, info, data):
        username = data.username
        user = User.objects.filter_by_username(username, is_active=True).first()
        if not user:
            return ResetUserPasswordVerify(
                errors={"error": "No active user present for username/email"},
                result=None,
                ok=False,
            )
        pin = data.pin
        current_time = timezone.now()
        password_reset_pin_object = PasswordResetPin.objects.filter(
            user=user,
            user__is_active=True,
            pin=pin,
            is_active=True,
            pin_expiry_time__gte=current_time,
        ).first()
        if not password_reset_pin_object:
            user_only_password_reset_object = PasswordResetPin.objects.filter(
                user=user
            ).first()
            if user_only_password_reset_object:
                user_only_password_reset_object.no_of_incorrect_attempts += 1
                user_only_password_reset_object.save()
                if not user.is_active:
                    return ResetUserPasswordVerify(
                        errors={"error": "User is inactive"},
                        result=None,
                        ok=False,
                    )
                elif user_only_password_reset_object.no_of_incorrect_attempts >= 5:
                    user.is_active = False
                    user.save()
                    return ResetUserPasswordVerify(
                        errors={
                            "error": "User is now inactive for trying too many times"
                        },
                        result=None,
                        ok=False,
                    )
                elif user_only_password_reset_object.pin != pin:
                    return ResetUserPasswordVerify(
                        error={"error": "Password reset pin is incorrect"},
                        result=None,
                        ok=False,
                    )
                else:
                    return ResetUserPasswordVerify(
                        errors={"error": "Password reset pin has expired"},
                        result=None,
                        ok=False,
                    )
            return ResetUserPasswordVerify(
                errors={"error": "No matching active user pin found"},
                result=None,
                ok=False,
            )
        else:
            password_reset_pin_object.no_of_incorrect_attempts = 0
            password_reset_pin_object.save()
            return ResetUserPasswordVerify(
                errors=None,
                result=password_reset_pin_object,
                ok=True,
            )


class PasswordResetChange(graphene.Mutation):
    class Arguments:
        data = PasswordResetChangeInput(
            description=_("Fields required to reset password."), required=True
        )

    errors = GenericScalar()
    ok = graphene.Boolean()
    result = GenericScalar()

    def mutate(self, info, data):
        username = data.username
        user = User.objects.filter_by_username(username, is_active=True).first()
        if not user:
            return PasswordResetChange(
                errors={"error": "No active user present for username/email"},
                result=None,
                ok=False,
            )
        identifier = data.identifier
        password = data.password
        re_password = data.re_password
        if re_password != password:
            return PasswordResetChange(
                errors={"error": "Password and re_password doesn't match"},
                result=None,
                ok=False,
            )
        current_time = timezone.now()
        password_reset_pin_object = PasswordResetPin.objects.filter(
            user=user,
            user__is_active=True,
            identifier=identifier,
            is_active=True,
            pin_expiry_time__gte=current_time,
        ).first()
        if not password_reset_pin_object:
            user_only_password_reset_object = PasswordResetPin.objects.filter(
                user=user
            ).first()
            if user_only_password_reset_object:
                user_only_password_reset_object.no_of_incorrect_attempts += 1
                user_only_password_reset_object.save()
                if not user.is_active:
                    return PasswordResetChange(
                        errors={"error": "User is inactive"},
                        result=None,
                        ok=False,
                    )
                elif user_only_password_reset_object.no_of_incorrect_attempts >= 5:
                    user.is_active = False
                    user.save()
                    return PasswordResetChange(
                        errors={
                            "error": "User is now inactive for trying too many times"
                        },
                        result=None,
                        ok=False,
                    )
                elif user_only_password_reset_object.identifier != identifier:
                    return PasswordResetChange(
                        errors={"error": "Password reset identifier is incorrect"},
                        result=None,
                        ok=False,
                    )
                else:
                    return PasswordResetChange(
                        errors={"error": "Password reset pin has expired"},
                        resut=None,
                        ok=False,
                    )
            return PasswordResetChange(
                errors={"error": "No matching active user pin found"},
                result=None,
                ok=False,
            )
        else:
            password_reset_pin_object.no_of_incorrect_attempts = 0
            password_reset_pin_object.is_active = False
            password_reset_pin_object.save()
            try:
                validate_password(password=password, user=user)
            except ValidationError as e:
                errors = list(e.messages)
                return PasswordResetChange(
                    errors={"errors": errors}, result=None, ok=False
                )
            user.set_password(password)
            user.save()
            return PasswordResetChange(
                result={"detail": "Password successfully changed"},
                errors=None,
                ok=True,
            )


class EmailConfirm(graphene.Mutation):
    class Arguments:
        data = EmailConfirmInput(
            description=_("Fields required to reset password."), required=True
        )

    errors = GenericScalar()
    ok = graphene.Boolean()
    result = GenericScalar()

    def mutate(self, info, data):
        user = User.objects.filter_by_username(data.username).first()
        if not user:
            return EmailConfirm(
                errors={"error": "No user present with given email address/username"},
                result=None,
                ok=True,
            )
        email_confirm_pin = EmailConfirmationPin.objects.filter(user=user).first()
        if email_confirm_pin:
            if email_confirm_pin.no_of_incorrect_attempts >= 5:
                return EmailConfirm(
                    errors={"error": "User is inactive for trying too many times"},
                    result=None,
                    ok=False,
                )
            if not email_confirm_pin.is_active:
                return EmailConfirm(
                    errors={"error": "Email address has already been confirmed"},
                    result=None,
                    ok=False,
                )
        random_6_digit_pin = gen_random_number(6)
        active_for_one_hour = timezone.now() + timezone.timedelta(hours=1)
        email_confirm_pin_object, _obj = EmailConfirmationPin.objects.update_or_create(
            user=user,
            defaults={
                "pin": random_6_digit_pin,
                "pin_expiry_time": active_for_one_hour,
                "is_active": True,
            },
        )
        template = get_template("mail/email_confirm.txt")
        context = {"user": user, "email_confirm_object": email_confirm_pin_object}
        message = template.render(context)
        user.email_user("Email confirmation mail", message)
        return EmailConfirm(
            result={"detail": "Email confirmation mail successfully send"},
            errors=None,
            ok=True,
        )


class EmailConfirmVerify(graphene.Mutation):
    class Arguments:
        data = EmailConfirmInput(
            description=_("Fields required to reset password."), required=True
        )

    errors = GenericScalar()
    ok = graphene.Boolean()
    result = GenericScalar()

    def mutate(self, info, data):
        user = User.objects.filter_by_username(data.username, is_active=False).first()
        if not user:
            return EmailConfirmVerify(
                errors={"error": "No inactive user present for username"},
                result=None,
                ok=False,
            )
        pin = data.pin
        current_time = timezone.now()
        email_confirmation_mail_object = EmailConfirmationPin.objects.filter(
            user=user,
            pin=pin,
            is_active=True,
            pin_expiry_time__gte=current_time,
        ).first()
        if not email_confirmation_mail_object:
            user_only_email_confirm_mail_object = EmailConfirmationPin.objects.filter(
                user=user
            ).first()
            if user_only_email_confirm_mail_object:
                if not user_only_email_confirm_mail_object.is_active:
                    return EmailConfirmVerify(
                        errors={"error": "Email is already confirmed for user"},
                        result=None,
                        ok=False,
                    )
                user_only_email_confirm_mail_object.no_of_incorrect_attempts += 1
                user_only_email_confirm_mail_object.save()
                if user_only_email_confirm_mail_object.no_of_incorrect_attempts >= 5:
                    return EmailConfirmVerify(
                        errors={
                            "error": "User is now inactive for trying too many times"
                        },
                        result=None,
                        ok=False,
                    )
                elif user_only_email_confirm_mail_object.pin != pin:
                    return EmailConfirmVerify(
                        errors={"error": "Email confirmation pin is incorrect"},
                        result=None,
                        ok=False,
                    )
                else:
                    return EmailConfirmVerify(
                        errors={"error": "Email confirmation pin has expired"},
                        result=None,
                        ok=False,
                    )
            return EmailConfirmVerify(
                errors={"error": "No matching active username/email found"},
                result=None,
                ok=False,
            )
        else:
            email_confirmation_mail_object.no_of_incorrect_attempts = 0
            email_confirmation_mail_object.is_active = False
            email_confirmation_mail_object.save()
            user.is_active = True
            user.save()
            return EmailConfirmVerify(
                result={"detail": "Email successfully confirmed"},
                errors=None,
                ok=True,
            )


class EmailChange(graphene.Mutation):
    class Arguments:
        data = EmailChangeInput(
            description=_("Fields required to reset password."), required=True
        )

    errors = GenericScalar()
    ok = graphene.Boolean()
    result = GenericScalar()

    def mutate(self, info, data):
        user = info.context.user
        email_change_pin = EmailChangePin.objects.filter(user=user).first()
        if email_change_pin:
            if email_change_pin.no_of_incorrect_attempts >= 5:
                return EmailChange(
                    errors={"error": "User is inactive for trying too many times"},
                    result=None,
                    ok=False,
                )
        random_6_digit_pin = gen_random_number(6)
        active_for_one_hour = timezone.now() + timezone.timedelta(hours=1)
        email_change_pin_object, _obj = EmailChangePin.objects.update_or_create(
            user=user,
            defaults={
                "pin": random_6_digit_pin,
                "pin_expiry_time": active_for_one_hour,
                "is_active": True,
                "new_email": data["new_email"],
            },
        )
        email_template = get_template("mail/email_change.txt")
        context = {"email_change_object": email_change_pin_object}
        message = email_template.render(context)
        send_mail(
            _("Email change mail"),
            message,
            from_email=None,
            recipient_list=[email_change_pin_object.new_email],
        )
        return EmailChange(
            result={"detail": "Email change mail successfully send"},
            errors=None,
            ok=True,
        )


class EmailChangeVerify(graphene.Mutation):
    class Arguments:
        data = EmailChangePinVerifyInput(
            description=_("Fields required to reset password."), required=True
        )

    errors = GenericScalar()
    ok = graphene.Boolean()
    result = GenericScalar()

    def mutate(self, info, data):
        user = info.context.user
        pin = data.pin
        current_time = timezone.now()
        email_change_mail_object = EmailChangePin.objects.filter(
            user=user,
            pin=pin,
            is_active=True,
            pin_expiry_time__gte=current_time,
        ).first()
        if not email_change_mail_object:
            user_only_email_change_mail_object = EmailChangePin.objects.filter(
                user=user
            ).first()
            if user_only_email_change_mail_object:
                if not user_only_email_change_mail_object.is_active:
                    return EmailChangeVerify(
                        errors={"error": "Email is already changed for user"},
                        result=None,
                        ok=False,
                    )
                user_only_email_change_mail_object.no_of_incorrect_attempts += 1
                user_only_email_change_mail_object.save()
                if user_only_email_change_mail_object.no_of_incorrect_attempts >= 5:
                    return EmailChangeVerify(
                        errors={
                            "error": "User is now inactive for trying too many times"
                        },
                        result=None,
                        ok=False,
                    )
                elif user_only_email_change_mail_object.pin != pin:
                    return EmailChangeVerify(
                        errors={"error": "Email change pin is incorrect"},
                        result=None,
                        ok=False,
                    )
                else:
                    return EmailChangeVerify(
                        errors={"error": "Email change pin has expired"},
                        result=None,
                        ok=False,
                    )
            return EmailChangeVerify(
                errors={"error": "No matching active change change request found"},
                result=None,
                ok=False,
            )
        else:
            email_change_mail_object.no_of_incorrect_attempts = 0
            email_change_mail_object.is_active = False
            email_change_mail_object.save()
            if User.objects.filter(email=email_change_mail_object.new_email).exists():
                return EmailChangeVerify(
                    errors={"error": "email already used for account creation"},
                    result=None,
                    ok=False,
                )
            user.email = email_change_mail_object.new_email
            user.save()
            return EmailChangeVerify(
                result={"detail": "Email successfully changed"},
                errors=None,
                ok=True,
            )
