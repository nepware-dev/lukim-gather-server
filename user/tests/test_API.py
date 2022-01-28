from django.apps import apps
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from graphql_jwt.shortcuts import get_token
from model_bakery import random_gen

from lukimgather.tests import TestBase


class APITest(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        users = cls.baker.make(settings.AUTH_USER_MODEL, is_active=True, _quantity=4)
        cls.activated_initial_password = get_user_model().objects.make_random_password()
        users[0].set_password(cls.activated_initial_password)
        users[0].save()
        cls.activated_user = authenticate(
            username=users[0].username, password=cls.activated_initial_password
        )
        cls.headers = {"HTTP_AUTHORIZATION": f"JWT {get_token(users[0])}"}

    def test_me_get(self):
        response = self.query(
            """
            query {
              me {
                id
                username
              }
            }
            """,
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)

    def test_user_change_password(self):
        user = self.baker.make(settings.AUTH_USER_MODEL, is_active=True)
        user_initial_password = get_user_model().objects.make_random_password()
        user.set_password(user_initial_password)
        user.save()
        new_password = get_user_model().objects.make_random_password()
        response = self.query(
            """
            mutation Mutation($input: ChangePasswordInput!) {
              changePassword(data: $input) {
                errors
                result
                ok
              }
            }
            """,
            input_data={
                "password": user_initial_password,
                "newPassword": new_password,
                "rePassword": new_password,
            },
            headers={"HTTP_AUTHORIZATION": f"JWT {get_token(user)}"},
        )
        self.assertEqual(response.status_code, 200)
        user = authenticate(username=user.username, password=new_password)
        self.assertIsNotNone(user)

    def test_user_email_verify(self):
        non_activated_user_pass = get_user_model().objects.make_random_password()
        non_activated_user_username = random_gen.gen_string(15)
        user_data = {
            "firstName": random_gen.gen_string(150),
            "lastName": random_gen.gen_string(150),
            "email": random_gen.gen_email(),
            "password": non_activated_user_pass,
            "rePassword": non_activated_user_pass,
            "username": non_activated_user_username,
        }
        response = self.query(
            """
            mutation Mutation($input: RegisterUserInput!) {
              registerUser(data: $input) {
                result {
                    username
                }
                errors
                ok
              }
            }
            """,
            input_data=user_data,
        )
        self.assertEqual(response.status_code, 200)
        non_activated_user = get_user_model().objects.get(
            username=non_activated_user_username
        )
        user = authenticate(
            username=non_activated_user.username, password=non_activated_user_pass
        )
        self.assertIsNone(user)
        email_verify_pin = (
            apps.get_model("user", "EmailConfirmationPin")
            .objects.get(user=non_activated_user)
            .pin
        )
        data = {
            "username": non_activated_user.username,
            "pin": email_verify_pin,
        }
        response = self.query(
            """
            mutation Mutation($input: EmailConfirmInput!) {
              emailConfirm(data: $input) {
                message
              }
            }
            """,
            input_data=data,
        )
        email_verified = get_user_model().objects.get(
            username=non_activated_user.username
        )
        self.assertTrue(email_verified.check_password(non_activated_user_pass))

    def test_password_reset_flow(self):
        user = self.baker.make(settings.AUTH_USER_MODEL, is_active=True)
        password_reset_mutation = """
            mutation Mutation($input: PasswordResetPinInput!) {
              passwordReset(data: $input) {
                result
                errors
                ok
              }
            }
        """
        password_reset_verify_mutation = """
            mutation Mutation($input: PasswordResetPinInput!) {
              passwordResetVerify(data: $input) {
                result {
                    identifier
                }
                errors
                ok
              }
            }
        """
        password_reset_change_mutation = """
            mutation Mutation($input: PasswordResetChangeInput!) {
              passwordResetChange(data: $input) {
                result
                errors
                ok
              }
            }
        """
        password_reset_response = self.query(
            password_reset_mutation, input_data={"username": user.username}
        )
        self.assertEqual(password_reset_response.status_code, 200)
        password_reset_pin = (
            apps.get_model("user", "PasswordResetPin").objects.get(user=user).pin
        )
        password_reset_verify_response = self.query(
            password_reset_verify_mutation,
            input_data={"username": user.username, "pin": password_reset_pin},
        )
        self.assertEqual(password_reset_verify_response.status_code, 200)
        identifier = password_reset_verify_response.json()["data"][
            "passwordResetVerify"
        ]["result"]["identifier"]
        new_pass = "secure^78@12"
        password_reset_change_response = self.query(
            password_reset_change_mutation,
            input_data={
                "username": user.username,
                "identifier": identifier,
                "password": new_pass,
                "rePassword": new_pass,
            },
        )
        self.assertEqual(password_reset_change_response.status_code, 200)
        user = authenticate(username=user.username, password=new_pass)
        self.assertIsNotNone(user)

    def test_email_change_flow(self):
        email_change_mutation = """
            mutation Mutation($input: EmailChangeInput!) {
              emailChange(data: $input) {
                errors
                result
                ok
              }
            }
        """
        email_change_verify_mutation = """
            mutation Mutation($input: EmailChangePinVerifyInput!) {
              emailChangeVerify(data: $input) {
                result
                errors
                ok
              }
            }
        """
        new_email = random_gen.gen_email().lower()
        email_change_data = {
            "newEmail": new_email,
            "password": self.activated_initial_password,
        }
        email_change_response = self.query(
            email_change_mutation, input_data=email_change_data, headers=self.headers
        )
        self.assertEqual(email_change_response.status_code, 200)
        email_change_pin = (
            apps.get_model("user", "EmailChangePin")
            .objects.get(user=self.activated_user)
            .pin
        )
        email_change_verify_data = {"pin": email_change_pin}
        email_change_verify_response = self.query(
            email_change_verify_mutation,
            input_data=email_change_verify_data,
            headers=self.headers,
        )
        self.assertEqual(email_change_verify_response.status_code, 200)
        user = get_user_model().objects.get(pk=self.activated_user.pk)
        self.assertEqual(new_email, user.email)
