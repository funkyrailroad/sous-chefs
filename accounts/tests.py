from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class UserTaskTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.email = "test@example.com"
        cls.password = "password"
        cls.first_name = "Frank"
        cls.last_name = "Johnson"

    def test_user_does_not_exist(self):
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(
                email=self.email,
                first_name=self.first_name,
                last_name=self.last_name,
            )

    def test_user_exists_after_registration(self):
        self.client.post(
            reverse("register"),
            data=dict(
                email=self.email,
                password=self.password,
                first_name=self.first_name,
                last_name=self.last_name,
            ),
        )

        User.objects.get(
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
        )
