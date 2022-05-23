import io
import json

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.gis import geos
from graphql_jwt.shortcuts import get_token
from PIL import Image

from lukimgather.tests import TestBase


class APITest(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        users = cls.baker.make(settings.AUTH_USER_MODEL, is_active=True, _quantity=1)
        cls.activated_initial_password = get_user_model().objects.make_random_password()
        users[0].set_password(cls.activated_initial_password)
        users[0].save()
        cls.category = cls.baker.make(
            "survey.ProtectedAreaCategory", title="test", _quantity=1
        )[0]
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

    def test_survey_get(self):
        response = self.query(
            """
            query {
              happeningSurveys {
                id
              }
            }
            """,
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)

    def test_categories_get(self):
        response = self.query(
            """
            query {
              protectedAreaCategories {
                id
                title
                child {
                  id
                  title
                }
              }
            }
            """,
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)

    def test_create_happening_survey(self):
        mutation = """
            mutation CreateHappeningSurvey($data: HappeningSurveyInput!) {
                createHappeningSurvey(data: $data) {
                    ok
                    result
                        {
                            id
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
                        "query": mutation,
                        "variables": {
                            "data": {
                                "title": "test title",
                                "description": "test description",
                                "sentiment": "\U0001f600",
                                "improvement": "INCREASING",
                                "location": str(geos.Point(1, 0)),
                                "categoryId": self.category.id,
                                "attachment": [None, None],
                            },
                        },
                    }
                ),
                "0": self.generate_photo_file(),
                "1": self.generate_photo_file(),
                "map": json.dumps(
                    {
                        "0": ["variables.data.attachment.0"],
                        "1": ["variables.data.attachment.1"],
                    }
                ),
            },
            **self.headers,
        )
        self.assertEqual(response.status_code, 200)

    def test_survey_form_get(self):
        response = self.query(
            """
            query {
              surveyForm {
                id
                code
                title
                xform
              }
            }
            """,
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)
