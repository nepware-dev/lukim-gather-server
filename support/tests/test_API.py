from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from graphql_jwt.shortcuts import get_token

from lukimgather.tests import TestBase


class APITest(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        users = cls.baker.make(settings.AUTH_USER_MODEL, is_active=True, _quantity=1)
        cls.activated_initial_password = get_user_model().objects.make_random_password()
        users[0].set_password(cls.activated_initial_password)
        users[0].save()
        cls.headers = {"HTTP_AUTHORIZATION": f"Bearer {get_token(users[0])}"}

    def test_legal_document_get(self):
        response = self.query(
            """
            query {
              legalDocument {
                id
                description
              }
            }
            """,
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)

    def test_create_feedback(self):
        response = self.query(
            """
            mutation CreateFeedback ($input: FeedbackMutationInput!) {
                createFeedback (input: $input) {
                    id
                }
            }
            """,
            input_data={"title": "test title", "description": "test description"},
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)

    def test_frequently_asked_question_get(self):
        response = self.query(
            """
            query {
              frequentlyAskedQuestion {
                id
                question
                answer
              }
            }
            """,
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)

    def test_resource_tag_get(self):
        response = self.query(
            """
            query {
              resourceTag {
                id
                title
              }
            }
            """,
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)

    def test_resource_get(self):
        response = self.query(
            """
            query {
              resource {
                id
                title
                description
                resourceType
                attachment
                videoUrl
              }
            }
            """,
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)
