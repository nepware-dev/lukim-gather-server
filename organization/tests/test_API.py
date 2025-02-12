from lukimgather.tests import TestBase


class APITest(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClassInit()

    def test_organization_get(self):
        response = self.query(
            """
            query {
              organizations {
                id
                title
                acronym
                description
                logo
                email
                phoneNumber
                pointOfContact
                website
                address
                membersCount
              }
            }
            """,
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)
