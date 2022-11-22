import graphene
import graphql_jwt
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from graphene.types.generic import GenericScalar
from graphene_django.rest_framework.mutation import SerializerMutation
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from graphql_jwt.refresh_token.shortcuts import create_refresh_token
from graphql_jwt.shortcuts import get_token
from phonenumber_field.validators import validate_international_phonenumber

from lukimgather.throttling import ratelimit
from lukimgather.utils import gen_random_number, gen_random_string
from support.models import EmailTemplate
from user.models import (
    EmailChangePin,
    EmailConfirmationPin,
    PasswordResetPin,
    PhoneNumberConfirmationPin,
    User,
)
from user.serializers import GrantSerializer
from user.types import PasswordResetPinType, PrivateUserType


class CustomObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(PrivateUserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user)


class UserInput(graphene.InputObjectType):
    first_name = graphene.String(description=_("First name"))
    last_name = graphene.String(description=_("Last name"))
    organization = graphene.String(description=_("Organization"), required=False)
    avatar = Upload(required=False)


class RegisterUserInput(graphene.InputObjectType):
    first_name = graphene.String(description=_("First Name"), required=True)
    last_name = graphene.String(description=_("Last Name"), required=True)
    email = graphene.String(description=_("Email"))
    phone_number = graphene.String(description=_("Phone Number"))
    password = graphene.String(description=_("Password"), required=False)
    re_password = graphene.String(description=_("Retype Password"), required=False)
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


class PhoneNumberConfirmInput(graphene.InputObjectType):
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
    result = graphene.Field(PrivateUserType)
    ok = graphene.Boolean()

    @ratelimit(key="ip", rate="500/h", block=True)
    @ratelimit(key="gql:data.username", rate="10/m", block=True)
    def mutate(self, info, data):
        user_exists = User.objects.filter_by_username(data.username).exists()
        if user_exists:
            raise GraphQLError("User with username/email already exists")
        user_password = None
        if "re_password" in data:
            user_password = data.pop("re_password")
        user_email = data.get("email")
        user_phone_number = data.get("phone_number")
        try:
            if user_email:
                validate_email(user_email)
            elif user_phone_number:
                validate_international_phonenumber(user_phone_number)
        except ValidationError as e:
            raise GraphQLError(e.message)
        if user_password:
            try:
                validate_password(password=user_password)
            except ValidationError as e:
                raise GraphQLError(e.message[0])
        user = User.objects.create_user(**data)
        user.is_active = True  # Note:- Temporary fix to remove 2 step verification
        user.save()
        return RegisterUser(result=user, ok=True, errors=None)


class ChangePassword(graphene.Mutation):
    class Arguments:
        data = ChangePasswordInput(
            description=_("Fields required to change password."), required=True
        )

    errors = GenericScalar()
    ok = graphene.Boolean()
    result = GenericScalar()

    @login_required
    def mutate(self, info, data):
        if not info.context.user.check_password(data.password):
            raise GraphQLError("Invalid password for user")
        user = User.objects.filter_by_username(
            info.context.user.username, is_active=True
        ).first()
        new_password = data.new_password
        re_new_password = data.re_password
        if re_new_password != new_password:
            raise GraphQLError("New password and re new password doesn't match")
        try:
            validate_password(password=new_password, user=user)
        except ValidationError as e:
            errors = list(e.messages)
            raise GraphQLError(errors)
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
    result = graphene.Field(PrivateUserType)

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
            raise GraphQLError(e)


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
            raise GraphQLError(
                "No active user present for username/email your account may be blocked"
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
        subject, html_message, text_message = EmailTemplate.objects.get(
            identifier="password_reset"
        ).get_email_contents(
            context={"user": user, "password_reset_object": password_reset_pin_object}
        )
        user.email_user(subject, text_message, html_message=html_message)
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
            raise GraphQLError("No active user present for username/email")
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
                    raise GraphQLError("User is inactive")
                elif user_only_password_reset_object.no_of_incorrect_attempts >= 5:
                    user.is_active = False
                    user.save()
                    raise GraphQLError("User is now inactive for trying too many times")
                elif user_only_password_reset_object.pin != pin:
                    raise GraphQLError("Password reset pin is incorrect")
                else:
                    raise GraphQLError("Password reset pin has expired")
            raise GraphQLError("No matching active user pin found")
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
            raise GraphQLError("No active user present for username/email")
        identifier = data.identifier
        password = data.password
        re_password = data.re_password
        if re_password != password:
            raise GraphQLError("Password and re_password doesn't match")
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
                    raise GraphQLError("User is inactive")
                elif user_only_password_reset_object.no_of_incorrect_attempts >= 5:
                    if user.is_active:
                        subject, html_message, text_message = EmailTemplate.objects.get(
                            identifier="account_blocked"
                        ).get_email_contents({"user": user})
                        user.email_user(
                            subject, text_message, html_message=html_message
                        )
                    user.is_active = False
                    user.save()
                    raise GraphQLError("User is now inactive for trying too many times")
                elif user_only_password_reset_object.identifier != identifier:
                    raise GraphQLError("Password reset identifier is incorrect")
                else:
                    raise GraphQLError("Password reset pin has expired")
            raise GraphQLError("No matching active user pin found")
        else:
            try:
                validate_password(password=password, user=user)
            except ValidationError as e:
                errors = list(e.messages)
                raise GraphQLError(errors[0])
            password_reset_pin_object.no_of_incorrect_attempts = 0
            password_reset_pin_object.is_active = False
            password_reset_pin_object.save()
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
            raise GraphQLError("No user present with given email address/username")
        email_confirm_pin = EmailConfirmationPin.objects.filter(user=user).first()
        if email_confirm_pin:
            if email_confirm_pin.no_of_incorrect_attempts >= 5:
                raise GraphQLError("User is inactive for trying too many times")
            if not email_confirm_pin.is_active:
                raise GraphQLError("Email address has already been confirmed")
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
        subject, html_message, text_message = EmailTemplate.objects.get(
            identifier="email_confirm"
        ).get_email_contents(
            {"user": user, "email_confirm_object": email_confirm_pin_object}
        )
        user.email_user(subject, text_message, html_message=html_message)
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
            raise GraphQLError("No inactive user present for username")
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
                    raise GraphQLError("Email is already confirmed for user")
                user_only_email_confirm_mail_object.no_of_incorrect_attempts += 1
                user_only_email_confirm_mail_object.save()
                if user_only_email_confirm_mail_object.no_of_incorrect_attempts >= 5:
                    raise GraphQLError("User is now inactive for trying too many times")
                elif user_only_email_confirm_mail_object.pin != pin:
                    raise GraphQLError("Email confirmation pin is incorrect")
                else:
                    raise GraphQLError("Email confirmation pin has expired")
            raise GraphQLError("No matching active username/email found")
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
                raise GraphQLError("User is inactive for trying too many times")
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
        subject, html_message, text_message = EmailTemplate.objects.get(
            identifier="email_change"
        ).get_email_contents({"email_change_object": email_change_pin_object})
        send_mail(
            subject,
            text_message,
            from_email=None,
            recipient_list=[email_change_pin_object.new_email],
            html_message=html_message,
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
                    raise GraphQLError("Email is already changed for user")
                user_only_email_change_mail_object.no_of_incorrect_attempts += 1
                user_only_email_change_mail_object.save()
                if user_only_email_change_mail_object.no_of_incorrect_attempts >= 5:
                    raise GraphQLError("User is now inactive for trying too many times")
                elif user_only_email_change_mail_object.pin != pin:
                    raise GraphQLError("Email change pin is incorrect")
                else:
                    raise GraphQLError("Email change pin has expired")
            raise GraphQLError("No matching active email change request found")
        else:
            if User.objects.filter(email=email_change_mail_object.new_email).exists():
                raise GraphQLError("email already used for account creation")
            email_change_mail_object.no_of_incorrect_attempts = 0
            email_change_mail_object.is_active = False
            email_change_mail_object.save()
            user.email = email_change_mail_object.new_email
            user.save()
            return EmailChangeVerify(
                result={"detail": "Email successfully changed"},
                errors=None,
                ok=True,
            )


class GrantMutation(SerializerMutation):
    class Meta:
        serializer_class = GrantSerializer
        fields = "__all__"


class PhoneNumberConfirm(graphene.Mutation):
    class Arguments:
        data = PhoneNumberConfirmInput(
            description=_("Fields required to confirm phone number."), required=True
        )

    errors = GenericScalar()
    ok = graphene.Boolean()
    result = GenericScalar()

    @ratelimit(key="ip", rate="500/h", block=True)
    @ratelimit(key="gql:data.username", rate="10/m", block=True)
    def mutate(self, info, data):
        user = User.objects.filter_by_username(data.username).first()
        if not user:
            raise GraphQLError("No user present with given phone number/username")
        active_for_five_minutes = timezone.now() + timezone.timedelta(minutes=5)
        phone_number_confirm_pin = PhoneNumberConfirmationPin.objects.filter(
            user=user, is_active=True, pin_expiry_time__lte=active_for_five_minutes
        ).first()
        if phone_number_confirm_pin:
            if phone_number_confirm_pin.no_of_incorrect_attempts >= 5:
                raise GraphQLError("User is inactive for trying too many times")
            raise GraphQLError("Confirmation SMS has already been sent")
        random_6_digit_pin = gen_random_number(6)
        (
            phone_number_confirm_pin_object,
            _obj,
        ) = PhoneNumberConfirmationPin.objects.update_or_create(
            user=user,
            defaults={
                "pin": random_6_digit_pin,
                "pin_expiry_time": active_for_five_minutes,
                "is_active": True,
            },
        )
        user.celery_sms_user(
            to=user.username,
            message=f"Your OTP is {random_6_digit_pin} for Lukim Gather, It will expire in next 5 minutes.",
        )
        return PhoneNumberConfirm(
            result={"detail": "Phone number confirmation SMS successfully send"},
            errors=None,
            ok=True,
        )


class PhoneNumberConfirmVerify(graphene.Mutation):
    class Arguments:
        data = PhoneNumberConfirmInput(
            description=_("Fields required to reset password."), required=True
        )

    user = graphene.Field(PrivateUserType)
    token = graphene.String()
    refresh_token = graphene.String()

    def mutate(self, info, data):
        user = User.objects.filter_by_username(data.username).first()
        if not user:
            raise GraphQLError("No inactive user present for username")
        pin = data.pin
        current_time = timezone.now()
        phone_number_confirmation_sms_object = (
            PhoneNumberConfirmationPin.objects.filter(
                user=user,
                pin=pin,
                is_active=True,
                pin_expiry_time__gte=current_time,
            ).first()
        )
        if not phone_number_confirmation_sms_object:
            user_only_phone_number_confirm_sms_object = (
                PhoneNumberConfirmationPin.objects.filter(user=user).first()
            )
            if user_only_phone_number_confirm_sms_object:
                if not user_only_phone_number_confirm_sms_object.is_active:
                    raise GraphQLError("Phone number is already confirmed for user")
                user_only_phone_number_confirm_sms_object.no_of_incorrect_attempts += 1
                user_only_phone_number_confirm_sms_object.save()
                if (
                    user_only_phone_number_confirm_sms_object.no_of_incorrect_attempts
                    >= 5
                ):
                    raise GraphQLError("User is now inactive for trying too many times")
                elif user_only_phone_number_confirm_sms_object.pin != pin:
                    raise GraphQLError("Phone number confirmation pin is incorrect")
                else:
                    raise GraphQLError("Phone number confirmation pin has expired")
            raise GraphQLError("No matching active username/phone number found")
        else:
            phone_number_confirmation_sms_object.no_of_incorrect_attempts = 0
            phone_number_confirmation_sms_object.is_active = False
            phone_number_confirmation_sms_object.save()
            return PhoneNumberConfirmVerify(
                token=get_token(user),
                refresh_token=create_refresh_token(user).token,
                user=user,
            )
