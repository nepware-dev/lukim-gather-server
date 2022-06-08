from django.test import RequestFactory
from django.urls import reverse
from graphene_django.utils.testing import GraphQLTestCase
from model_bakery import baker, random_gen


class TestBase(GraphQLTestCase):
    baker = baker
    baker.generators.add("lukimgather.fields.LowerCharField", random_gen.gen_string)
    baker.generators.add("lukimgather.fields.LowerEmailField", random_gen.gen_email)
    factory = RequestFactory()
    fixtures = ["support/content/email.yaml"]
    GRAPHQL_URL = reverse("api")
