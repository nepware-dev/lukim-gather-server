from lukimgather.tests import TestBase


class APITest(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClassInit()

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

    def test_account_delete_requestion(self):
        response = self.query(
            """
            mutation DeleteAccount($input: AccountDeletionRequestMutationInput!) {
              deleteAccount(input: $input) {
                reason
                clientMutationId
              }
            }
            """,
            input_data={"reason": "test"},
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)

    def test_contact_us(self):
        response = self.query(
            """
            mutation ContactUs($input: ContactUsMutationInput!) {
              contactUs(input: $input) {
                name
                email
                subject
                message
              }
            }
            """,
            input_data={
                "name": "test",
                "email": "test@mail.com",
                "subject": "test",
                "message": "test",
            },
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)
