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
        survey = cls.baker.make("survey.HappeningSurvey", _quantity=5)
        comment = cls.baker.make("discussion.Comment", _quantity=5)
        cls.survey = survey.pop()
        cls.comment = comment.pop()
        cls.headers = {"HTTP_AUTHORIZATION": f"Bearer {get_token(users[0])}"}

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
