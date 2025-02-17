from lukimgather.tests import TestBase


class APITest(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClassInit(is_staff=True)
        cls.projects = cls.baker.make(
            "project.Project", title="test project title", make_m2m=True
        )

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
                ok
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
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)

    def test_delete_project_user(self):
        response = self.query(
            """
            mutation DeleteProjectUser($userId: ID!, $projectId: ID!) {
              deleteProjectUser(userId: $userId, projectId: $projectId) {
                ok
                errors
              }
            }
            """,
            variables={
                "userId": self.projects.users.first().id,
                "projectId": self.projects.id,
            },
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)
