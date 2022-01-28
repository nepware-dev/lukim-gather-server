from django.conf import settings
from django.contrib.auth import get_user_model

from lukimgather.tests import TestBase


class APITest(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = cls.baker.make(
            settings.AUTH_USER_MODEL,
            is_superuser=True,
            is_active=True,
        )
        cls.user_pass = get_user_model().objects.make_random_password()
        user.set_password(cls.user_pass)
        user.save()
        cls.user = user

    def test_username_jwt_login(self):
        response = self.query(
            """
            mutation {
              tokenAuth(username: "%s", password: "%s") {
                token
                payload
                refreshExpiresIn
              }
            }
            """
            % (self.user.username, self.user_pass),
        )
        self.assertEqual(response.status_code, 200)
