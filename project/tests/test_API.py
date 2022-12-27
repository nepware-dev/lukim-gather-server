from django.conf import settings
from django.contrib.auth import get_user_model
from graphql_jwt.shortcuts import get_token

from lukimgather.tests import TestBase
from project.models import Project


class APITest(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        users = cls.baker.make(settings.AUTH_USER_MODEL, is_active=True, _quantity=1)
        cls.activated_initial_password = get_user_model().objects.make_random_password()
        cls.projects = cls.baker.make(
            "project.Project", title="test project title", make_m2m=True
        )
        cls.users = users
        users[0].set_password(cls.activated_initial_password)
        users[0].save()
        cls.headers = {"HTTP_AUTHORIZATION": f"Bearer {get_token(users[0])}"}

    def test_organization_get(self):
        response = self.query(
            """
            query {
              projects {
                id
                title
                description
                organization {
                  id
                }
              }
            }
            """,
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)

    def test_add_project_user(self):
        response = self.query(
            """
            mutation AddProjectUser($input: AddProjectUserMutationInput!) {
              addProjectUser(input: $input) {
                id
                errors {
                  field
                  messages
                }
              }
            }
            """,
            input_data={
                "id": self.projects.id,
                "users": [user.id for user in self.users],
            },
        )
        self.assertResponseNoErrors(response)

    def test_delete_project_user(self):
        response = self.query(
            """
            mutation DeleteProjectUser($id: ID!) {
              deleteProjectUser(id: $id) {
                ok
                errors
              }
            }
            """,
            variables={"id": self.projects.users.first().id},
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)
