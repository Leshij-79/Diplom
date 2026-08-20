from django.core import mail
from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser


class UserLogoutViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@test.ru",
            first_name="Test",
            last_name="User",
            middle_name="User",
            phone_number="71234567890",
        )

    def test_logout(self):
        url = reverse("users:logout")

        self.client.login(username="test@test.ru", password="testpass123")

        response = self.client.post(url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("meddiag:index"))


class UserLoginViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@test.ru",
            first_name="Test",
            last_name="User",
            middle_name="User",
            phone_number="71234567890",
        )

    def test_login(self):
        url = reverse("users:login")

        self.client.login(username="test@test.ru", password="testpass123")

        data = {
            "username": "test@test.ru",
            "password": "testpass123",
        }

        response = self.client.post(url, data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)

    def test_login_with_invalid_credentials(self):
        url = reverse("users:login")

        data = {
            "username": "test@test.ru",
            "password": "123",
        }

        response = self.client.post(url, data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_authenticated)


class RegisterViewTest(TestCase):
    def test_register(self):
        url = reverse("users:register")

        data = {
            "username": "testuser",
            "password1": "testpass123",
            "password2": "testpass123",
            "email": "test@test.ru",
            "first_name": "Test",
            "last_name": "User",
            "middle_name": "User",
            "phone_number": "71234567890",
            "is_active": False,
        }

        response = self.client.post(url, data, follow=True)

        self.assertEqual(response.status_code, 200)

        user = CustomUser.objects.filter(username="testuser").first()

        self.assertIsNotNone(user)
        self.assertFalse(user.is_active)
        self.assertIsNotNone(user.token)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Авторизация на сайте")
        self.assertEqual(mail.outbox[0].to[0], user.email)

    def test_email_verification(self):
        user = CustomUser.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@test.ru",
            first_name="Test",
            last_name="User",
            middle_name="User",
            phone_number="71234567890",
            is_active=False,
            token="TestToken",
        )

        url = reverse("users:email-confirm", kwargs={"token": "TestToken"})

        response = self.client.get(url, follow=True)

        self.assertRedirects(response, reverse("users:login"))

        user.refresh_from_db()
        self.assertTrue(user.is_active)
