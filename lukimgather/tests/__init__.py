import secrets
import string

from django.conf import settings
from django.contrib.auth import authenticate
from django.test import RequestFactory
from django.urls import reverse
from graphene_django.utils.testing import GraphQLTestCase
from graphql_jwt.shortcuts import get_token
from model_bakery import baker, random_gen


class TestBase(GraphQLTestCase):
    baker = baker
    baker.generators.add("lukimgather.fields.LowerCharField", random_gen.gen_string)
    baker.generators.add("lukimgather.fields.LowerEmailField", random_gen.gen_email)
    factory = RequestFactory()
    fixtures = ["support/content/email.yaml"]
    GRAPHQL_URL = reverse("api")

    @staticmethod
    def make_random_password(length=20):
        alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
        password = "".join(secrets.choice(alphabet) for i in range(length))
        return password

    @classmethod
    def setUpClassInit(
        self,
        is_active=True,
        is_staff=False,
        is_superuser=False,
        _quantity=1,
    ):
        super().setUpClass()

        self.users = self.baker.make(
            settings.AUTH_USER_MODEL,
            is_active=True,
            is_staff=is_staff,
            is_superuser=is_superuser,
            _quantity=_quantity,
        )

        first_user = self.users[0]
        self.activated_initial_password = self.make_random_password()
        first_user.set_password(self.activated_initial_password)
        first_user.save()
        self.activated_user = authenticate(
            username=first_user.username, password=self.activated_initial_password
        )
        self.activated_user_token = get_token(self.activated_user)
        self.headers = {"Authorization": f"Bearer {self.activated_user_token}"}
        self.http_headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.activated_user_token}"
        }
