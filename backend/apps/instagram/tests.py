import json

from apps.instagram.models import Followers
from apps.users.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient


class InstagramTrackingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username="tester")
        self.user.set_password("test-password")
        self.user.save(update_fields=["password"])
        self.client.force_authenticate(user=self.user)

    def _followers_file(self, usernames: list[str], filename: str = "followers.json"):
        payload = [
            {
                "title": "",
                "media_list_data": [],
                "string_list_data": [
                    {
                        "href": f"https://www.instagram.com/{username}",
                        "value": username,
                        "timestamp": 1753815733,
                    }
                ],
            }
            for username in usernames
        ]
        return SimpleUploadedFile(
            filename,
            json.dumps(payload).encode("utf-8"),
            content_type="application/json",
        )

    def _following_file(self, usernames: list[str], filename: str = "following.json"):
        payload = {
            "relationships_following": [
                {
                    "title": "",
                    "media_list_data": [],
                    "string_list_data": [
                        {
                            "href": f"https://www.instagram.com/{username}",
                            "value": username,
                            "timestamp": 1753815733,
                        }
                    ],
                }
                for username in usernames
            ]
        }
        return SimpleUploadedFile(
            filename,
            json.dumps(payload).encode("utf-8"),
            content_type="application/json",
        )

    def test_lost_followers_initializes_baseline_on_first_upload(self):
        response = self.client.post(
            "/contacts/tracking/lost-followers",
            {"file": self._followers_file(["alice", "bob"])},
            format="multipart",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["baseline_initialized"])
        self.assertEqual(response.data["lost_followers"], [])
        self.assertEqual(Followers.objects.filter(user=self.user).count(), 2)

    def test_lost_followers_returns_missing_accounts_after_baseline_exists(self):
        self.client.post(
            "/contacts/tracking/lost-followers",
            {"file": self._followers_file(["alice", "bob"])},
            format="multipart",
        )

        response = self.client.post(
            "/contacts/tracking/lost-followers",
            {"file": self._followers_file(["alice"])},
            format="multipart",
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["baseline_initialized"])
        lost_usernames = {item["username"] for item in response.data["lost_followers"]}
        self.assertEqual(lost_usernames, {"bob"})

    def test_submit_followers_overrides_snapshot_for_user(self):
        self.client.post(
            "/contacts/tracking/followers/submit",
            {"file": self._followers_file(["alice", "bob"])},
            format="multipart",
        )

        response = self.client.post(
            "/contacts/tracking/followers/submit",
            {"file": self._followers_file(["carol"])},
            format="multipart",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_followers"], 1)
        usernames = set(
            Followers.objects.filter(user=self.user).values_list("follower__username", flat=True)
        )
        self.assertEqual(usernames, {"carol"})

    def test_non_followers_returns_following_minus_followers_snapshot(self):
        self.client.post(
            "/contacts/tracking/followers/submit",
            {"file": self._followers_file(["alice", "bob"])},
            format="multipart",
        )

        response = self.client.post(
            "/contacts/tracking/non-followers",
            {"file": self._following_file(["alice", "bob", "david"])},
            format="multipart",
        )

        self.assertEqual(response.status_code, 200)
        non_followers = {item["username"] for item in response.data["non_followers"]}
        self.assertEqual(non_followers, {"david"})
