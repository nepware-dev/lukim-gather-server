from django.conf import settings
from django.contrib.auth import get_user_model
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
        notifications = cls.baker.make(
            "notification.Notification", recipient=users[0], _quantity=5
        )
        cls.notification = notifications.pop()

    def test_get_notice(self):
        response = self.query(
            """
            query {
                notice {
                    id
                    title
                    description
                    isActive
                }
            }
            """,
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)

    def test_get_notification_unread_count(self):
        response = self.query(
            """
                query {
                    notificationUnreadCount
                }
            """,
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)

    def test_notification_mark_as_read(self):
        response = self.query(
            """
                mutation MarkAsRead($id: Int){
                    markAsRead(pk: $id) {
                        detail
                    }
                }
            """,
            input_data={"id": self.notification.pk},
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)

    def test_notification_mark_all_as_read(self):
        response = self.query(
            """
                mutation {
                    markAsRead(all:true) {
                        detail
                    }
                }
            """,
            input_data={"all": "true"},
            headers=self.headers,
        )
        self.assertResponseNoErrors(response)
