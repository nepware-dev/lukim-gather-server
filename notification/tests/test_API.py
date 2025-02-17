from lukimgather.tests import TestBase


class APITest(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClassInit()
        notifications = cls.baker.make(
            "notification.Notification", recipient=cls.activated_user, _quantity=5
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
