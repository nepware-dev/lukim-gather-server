import io
import json
from unittest import skip

from django.apps import apps
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from graphql_jwt.shortcuts import get_token
from model_bakery import random_gen
from PIL import Image

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
        cls.headers = {"HTTP_AUTHORIZATION": f"Bearer {get_token(users[0])}"}

    def generate_photo_file(self):
        file = io.BytesIO()
        image = Image.new("RGBA", size=(100, 100), color=(155, 0, 0))
        image.save(file, "png")
        file.name = "test.png"
        file.seek(0)
        return file

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

    def test_get_users(self):
        response = self.query(
            """
            query Users($search: String!) {
              users(search: $search) {
                id
                firstName
                lastName
              }
            }
            """,
            variables={"search": "name"},
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)

    def test_user_update(self):
        avatar = self.generate_photo_file()
        query = """
            mutation UpdateUser($data: UserInput!) {
              updateUser(data: $data) {
                ok
                result {
                  organization
                }
                errors
              }
            }
            """
        response = self.client.post(
            self.GRAPHQL_URL,
            data={
                "operations": json.dumps(
                    {
                        "query": query,
                        "variables": {"data": {"organization": "test", "avatar": None}},
                    }
                ),
                "t_file": avatar,
                "map": json.dumps(
                    {
                        "t_file": ["variables.data.avatar"],
                    }
                ),
            },
            **self.headers,
        )
        self.assertEqual(response.status_code, 200)

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
            headers={"HTTP_AUTHORIZATION": f"Bearer {get_token(user)}"},
        )
        self.assertEqual(response.status_code, 200)
        user = authenticate(username=user.username, password=new_password)
        self.assertIsNotNone(user)

    @skip("Temporarily skip 2 step email verification test")
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
                result
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
            mutation EmailChangeMutation($input: EmailChangeInput!) {
              emailChange(data: $input) {
                errors
                result
                ok
              }
            }
        """
        email_change_verify_mutation = """
            mutation EmailChangeVerifyMutation($input: EmailChangePinVerifyInput!) {
              emailChangeVerify(data: $input) {
                result
                errors
                ok
              }
            }
        """
        new_email = "new_email@address.com"
        email_change_data = {
            "newEmail": new_email,
            "option": "CHANGE",
        }
        email_change_response = self.query(
            email_change_mutation, input_data=email_change_data, headers=self.headers
        )
        self.assertResponseNoErrors(email_change_response)
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

    def test_phone_number_change_flow(self):
        phone_number_change_mutation = """
            mutation Mutation($input: PhoneNumberChangeInput!) {
              phoneNumberChange(data: $input) {
                errors
                result
                ok
              }
            }
        """
        phone_number_change_verify_mutation = """
            mutation Mutation($input: PhoneNumberChangePinVerifyInput!) {
              phoneNumberChangeVerify(data: $input) {
                result
                errors
                ok
              }
            }
        """
        new_phone_number = "+33612345678"
        phone_number_change_data = {
            "newPhoneNumber": new_phone_number,
        }
        phone_number_change_response = self.query(
            phone_number_change_mutation,
            input_data=phone_number_change_data,
            headers=self.headers,
        )
        self.assertResponseNoErrors(phone_number_change_response)
        phone_number_change_pin = (
            apps.get_model("user", "PhoneNumberChangePin")
            .objects.get(user=self.activated_user)
            .pin
        )
        phone_number_change_verify_data = {"pin": phone_number_change_pin}
        phone_number_change_verify_response = self.query(
            phone_number_change_verify_mutation,
            input_data=phone_number_change_verify_data,
            headers=self.headers,
        )
        self.assertResponseNoErrors(phone_number_change_verify_response)
        user = get_user_model().objects.get(pk=self.activated_user.pk)
        self.assertEqual(new_phone_number, user.phone_number)

    def test_user_grant_get(self):
        response = self.query(
            """
            query {
              grant {
                id
                title
                user {
                    id
                    username
                }
              }
            }
            """,
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)

    def test_create_user_grant(self):
        response = self.query(
            """
            mutation Mutation($input: GrantMutationInput!) {
              createGrant(input: $input) {
                id
                title
                errors {
                  field
                  messages
                }
              }
            }
            """,
            input_data={
                "title": "test title",
                "description": "test description",
                "user": self.activated_user.username,
            },
        )
        self.assertResponseNoErrors(response)

    def test_user_phone_number_verify(self):
        non_activated_user_pass = get_user_model().objects.make_random_password()
        non_activated_user_username = random_gen.gen_string(15)
        user_data = {
            "firstName": random_gen.gen_string(150),
            "lastName": random_gen.gen_string(150),
            "phoneNumber": "+33612345678",
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
        self.assertResponseNoErrors(response)
        non_activated_user = get_user_model().objects.get(
            username=non_activated_user_username
        )
        user = authenticate(
            username=non_activated_user.username, password=non_activated_user_pass
        )
        self.assertIsNone(user)
        phone_number_verify_pin = (
            apps.get_model("user", "PhoneNumberConfirmationPin")
            .objects.get(user=non_activated_user)
            .pin
        )
        data = {
            "username": non_activated_user.username,
            "pin": phone_number_verify_pin,
        }
        response = self.query(
            """
            mutation Mutation($input: PhoneNumberConfirmInput!) {
              phoneNumberVerify(data: $input) {
                token
                refreshToken
                user {
                    id
                    firstName
                    lastName
                    email
                    organization
                    avatar
                }
              }
            }
            """,
            input_data=data,
        )
        self.assertResponseNoErrors(response)
