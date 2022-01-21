import graphene
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.template.loader import get_template
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from lukimgather.utils import gen_random_number, gen_random_string
from user.models import EmailChangePin, EmailConfirmationPin, PasswordResetPin, User
from user.types import UserType


class RegisterUserInput(graphene.InputObjectType):
    first_name = graphene.String(description=_("First Name"), required=True)
    last_name = graphene.String(description=_("Last Name"), required=True)
    email = graphene.String(description=_("Email"), required=True)
    password = graphene.String(description=_("Password"), required=True)
    re_password = graphene.String(description=_("Retype Password"), required=True)
    username = graphene.String(description=_("Username"), required=True)


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
    pin_expiry_time = graphene.DateTime(description=_("Pin Expiry Time"))
    new_email = graphene.String(description=_("New Email"))
    is_active = graphene.Boolean(description=_("Is Active"))


class RegisterUser(graphene.Mutation):
    user = graphene.Field(UserType, required=True)

    class Arguments:
        data = RegisterUserInput(
            description=_("Fields required to create a user."), required=True
        )

    def mutate(self, info, data):
        user_exists = User.objects.filter_by_username(data.username).exists()
        if user_exists:
            raise ValidationError(
                {_("error"): _("User with username/email already exists")},
            )
        user_password = data.pop("re_password")
        try:
            validate_password(password=user_password)
        except ValidationError as e:
            errors = list(e.messages)
            raise ValidationError({_("errors"): errors})
        user = User.objects.create_user(**data)
        return RegisterUser(user=user)


class ChangePassword(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        data = PasswordResetChangeInput(
            description=_("Fields required to change password."), required=True
        )

    def mutate(self, info, data):
        user = User.objects.filter_by_username(
            self.request.user, is_active=True
        ).first()
        new_password = data.new_password
        re_new_password = data.re_new_password
        if re_new_password != new_password:
            raise ValidationError(
                {_("error"): _("New password and re new password doesn't match")},
            )
        user.set_password(new_password)
        user.save()
        return ChangePassword(message={_("detail"): _("Password successfully updated")})


class ResetUserPassword(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        data = PasswordResetPinInput(
            description=_("Fields required to reset password."), required=True
        )

    def mutate(self, info, data):
        username = data.username
        user = User.objects.filter_by_username(username, is_active=True).first()
        if not user:
            raise ValidationError(
                {
                    _("error"): _(
                        "No active user present for username/email your account may be blocked"
                    )
                },
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
            message={_("detail"): _("Password reset email successfully send")}
        )


class ResetUserPasswordVerify(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        data = PasswordResetPinInput(
            description=_("Fields required to reset password."), required=True
        )

    def mutate(self, info, data):
        username = data.username
        user = User.objects.filter_by_username(username, is_active=True).first()
        if not user:
            raise ValidationError(
                {_("error"): _("No active user present for username/email")},
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
                    raise ValidationError(
                        {_("error"): _("User is inactive")},
                    )
                elif user_only_password_reset_object.no_of_incorrect_attempts >= 5:
                    user.is_active = False
                    user.save()
                    raise ValidationError(
                        {
                            _("error"): _(
                                "User is now inactive for trying too many times"
                            )
                        },
                    )
                elif user_only_password_reset_object.pin != pin:
                    raise ValidationError(
                        {_("error"): _("Password reset pin is incorrect")},
                    )
                else:
                    raise ValidationError(
                        {_("error"): _("Password reset pin has expired")},
                    )
            raise ValidationError(
                {_("error"): _("No matching active user pin found")},
            )
        else:
            password_reset_pin_object_identifier = password_reset_pin_object.identifier
            password_reset_pin_object.no_of_incorrect_attempts = 0
            password_reset_pin_object.save()
            return ResetUserPasswordVerify(
                message={"identifier": password_reset_pin_object_identifier}
            )


class PasswordResetChange(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        data = PasswordResetChangeInput(
            description=_("Fields required to reset password."), required=True
        )

    def mutate(self, info, data):
        username = data.username
        user = User.objects.filter_by_username(username, is_active=True).first()
        if not user:
            raise ValidationError(
                {_("error"): _("No active user present for username/email")}
            )
        identifier = data.identifier
        password = data.password
        re_password = data.re_password
        if re_password != password:
            raise ValidationError(
                {_("error"): _("Password and re_password doesn't match")}
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
                    raise ValidationError(
                        {_("error"): _("User is inactive")},
                    )
                elif user_only_password_reset_object.no_of_incorrect_attempts >= 5:
                    user.is_active = False
                    user.save()
                    raise ValidationError(
                        {
                            _("error"): _(
                                "User is now inactive for trying too many times"
                            )
                        },
                    )
                elif user_only_password_reset_object.identifier != identifier:
                    raise ValidationError(
                        {_("error"): _("Password reset identifier is incorrect")},
                    )
                else:
                    raise ValidationError(
                        {_("error"): _("Password reset pin has expired")},
                    )
            raise ValidationError(
                {_("error"): _("No matching active user pin found")},
            )
        else:
            password_reset_pin_object.no_of_incorrect_attempts = 0
            password_reset_pin_object.is_active = False
            password_reset_pin_object.save()
            try:
                validate_password(password=password, user=user)
            except ValidationError as e:
                errors = list(e.messages)
                raise ValidationError({_("errors"): errors})
            user.set_password(password)
            user.save()
            return PasswordResetChange(
                message={_("detail"): _("Password successfully changed")}
            )


class EmailConfirm(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        data = EmailConfirmInput(
            description=_("Fields required to reset password."), required=True
        )

    def mutate(self, info, data):
        user = User.objects.filter_by_username(data.username).first()
        if not user:
            raise ValidationError(
                {_("error"): _("No user present with given email address/username")}
            )
        email_confirm_pin = EmailConfirmationPin.objects.filter(user=user).first()
        if email_confirm_pin:
            if email_confirm_pin.no_of_incorrect_attempts >= 5:
                raise ValidationError(
                    {_("error"): _("User is inactive for trying too many times")},
                )
            if not email_confirm_pin.is_active:
                raise ValidationError(
                    {_("error"): _("Email address has already been confirmed")},
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
            message={_("detail"): _("Email confirmation mail successfully send")}
        )


class EmailConfirmVerify(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        data = EmailConfirmInput(
            description=_("Fields required to reset password."), required=True
        )

    def mutate(self, info, data):
        user = User.objects.filter_by_username(data.username, is_active=False).first()
        if not user:
            raise ValidationError(
                {_("error"): _("No inactive user present for username")},
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
                    raise ValidationError(
                        {_("error"): _("Email is already confirmed for user")},
                    )
                user_only_email_confirm_mail_object.no_of_incorrect_attempts += 1
                user_only_email_confirm_mail_object.save()
                if user_only_email_confirm_mail_object.no_of_incorrect_attempts >= 5:
                    raise ValidationError(
                        {
                            _("error"): _(
                                "User is now inactive for trying too many times"
                            )
                        },
                    )
                elif user_only_email_confirm_mail_object.pin != pin:
                    raise ValidationError(
                        {_("error"): _("Email confirmation pin is incorrect")},
                    )
                else:
                    raise ValidationError(
                        {_("error"): _("Email confirmation pin has expired")},
                    )
            raise ValidationError(
                {_("error"): _("No matching active username/email found")},
            )
        else:
            email_confirmation_mail_object.no_of_incorrect_attempts = 0
            email_confirmation_mail_object.is_active = False
            email_confirmation_mail_object.save()
            user.is_active = True
            user.save()
            return EmailConfirmVerify(
                message={_("detail"): _("Email successfully confirmed")}
            )


class EmailChange(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        data = EmailChangePinInput(
            description=_("Fields required to reset password."), required=True
        )

    def mutate(self, info, data):
        user = info.context.user
        email_change_pin = EmailChangePin.objects.filter(user=user).first()
        if email_change_pin:
            if email_change_pin.no_of_incorrect_attempts >= 5:
                raise ValidationError(
                    {_("error"): _("User is inactive for trying too many times")},
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
            "Email change mail",
            message,
            from_email=None,
            recipient_list=[email_change_pin_object.new_email],
        )
        return EmailChange(
            message={_("detail"): _("Email change mail successfully send")}
        )


class EmailChangeVerify(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        data = EmailChangePinInput(
            description=_("Fields required to reset password."), required=True
        )

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
                    raise ValidationError(
                        {_("error"): _("Email is already changed for user")},
                    )
                user_only_email_change_mail_object.no_of_incorrect_attempts += 1
                user_only_email_change_mail_object.save()
                if user_only_email_change_mail_object.no_of_incorrect_attempts >= 5:
                    raise ValidationError(
                        {
                            _("error"): _(
                                "User is now inactive for trying too many times"
                            )
                        },
                    )
                elif user_only_email_change_mail_object.pin != pin:
                    raise ValidationError(
                        {_("error"): _("Email change pin is incorrect")},
                    )
                else:
                    raise ValidationError(
                        {_("error"): _("Email change pin has expired")},
                    )
            raise ValidationError(
                {_("error"): _("No matching active change change request found")},
            )
        else:
            email_change_mail_object.no_of_incorrect_attempts = 0
            email_change_mail_object.is_active = False
            email_change_mail_object.save()
            if User.objects.filter(email=email_change_mail_object.new_email).exists():
                raise ValidationError(
                    {_("error"): _("email already used for account creation")},
                )
            user.email = email_change_mail_object.new_email
            user.save()
            return EmailChangeVerify(
                message={_("detail"): _("Email successfully changed")}
            )
