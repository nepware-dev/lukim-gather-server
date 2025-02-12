from lukimgather.tests import TestBase


class APITest(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClassInit()
        survey = cls.baker.make("survey.HappeningSurvey", _quantity=5)
        comment = cls.baker.make("discussion.Comment", _quantity=5)
        cls.survey = survey.pop()
        cls.comment = comment.pop()

    def test_create_comment(self):
        response = self.query(
            """
            mutation CreateComment($input: CommentMutationInput!) {
                createComment(input: $input) {
                    id
                    description
                    errors {
                        field
                        messages
                    }
                }
            }
            """,
            input_data={
                "objectId": str(self.survey.id),
                "description": "test comment",
                "contentType": "happeningsurvey",
            },
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)

    def test_get_comment(self):
        response = self.query(
            """
            query Comments($surveyId: String!, $level: Int) {
                comments(objectId: $surveyId, level: $level) {
                    id
                    createdAt
                    description
                    totalLikes
                    hasLiked
                    user {
                        firstName
                        lastName
                        avatar
                    }
                    replies {
                        description
                        user {
                            firstName
                            lastName
                            avatar
                        }
                        createdAt
                    }
                }
            }
            """,
            variables={"surveyId": str(self.survey.id), "level": 0},
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)

    def test_update_comment(self):
        response = self.query(
            """
            mutation UpdateComment($input: UpdateCommentInput!) {
              updateComment(input: $input) {
                ok
                errors {
                  field
                  messages
                }
              }
            }
            """,
            input_data={"id": self.comment.id, "message": "test update comment"},
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)

    def test_like_comment(self):
        response = self.query(
            """
            mutation LikeComment($input: LikeCommentMutationInput!) {
                likeComment(input: $input) {
                    id
                    errors {
                        field
                        messages
                    }
                }
            }
            """,
            input_data={"comment": str(self.comment.id)},
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)

    def test_dislike_comment(self):
        response = self.query(
            """
            mutation DislikeComment($id: Int!) {
                dislikeComment(id: $id) {
                    ok
                    errors
                }
            }
            """,
            variables={"id": self.comment.id},
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)

    def test_delete_comment(self):
        response = self.query(
            """
            mutation DislikeComment($id: ID!) {
              deleteComment(id: $id) {
                ok
                errors {
                  field
                  messages
                }
              }
            }
            """,
            variables={"id": self.comment.id},
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)
