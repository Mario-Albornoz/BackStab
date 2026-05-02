from apps.users.models import User
from django.test import TestCase
from rest_framework.test import APIClient


class AuthApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_signup_creates_user(self):
        response = self.client.post(
            "/api/auth/signup/",
            {"username": "newuser", "password": "strongpass123"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_returns_access_and_refresh_tokens(self):
        user = User.objects.create(username="loginuser")
        user.set_password("strongpass123")
        user.save(update_fields=["password"])

        response = self.client.post(
            "/api/auth/login/",
            {"username": "loginuser", "password": "strongpass123"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
