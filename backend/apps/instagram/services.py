import json
from dataclasses import dataclass
from datetime import datetime, timezone

from apps.instagram.models import Contact, Followers
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

User = get_user_model()


@dataclass
class InstagramContact:
    link_to_account: str
    username: str
    timestamp: int


class LostFollowersService:
    @staticmethod
    def _normalize_identity(link_to_account: str, username: str) -> str:
        # Prefer profile link as stable identity to survive username changes.
        normalized_link = (link_to_account or "").strip().rstrip("/").lower()
        if normalized_link:
            return normalized_link
        return username.strip().lower()

    def _extract_entries_from_rows(self, rows: list[dict]) -> list[InstagramContact]:
        contacts: list[InstagramContact] = []
        for item in rows:
            for entry in item.get("string_list_data", []):
                contacts.append(
                    InstagramContact(
                        link_to_account=entry["href"],
                        username=entry["value"],
                        timestamp=entry["timestamp"],
                    )
                )
        return contacts

    def extract_followers_from_json(self, file: UploadedFile) -> list[InstagramContact]:
        try:
            parsed_json = json.load(file)
            file.seek(0)
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON file.") from exc

        if not isinstance(parsed_json, list):
            raise ValueError("Followers file must be a JSON array.")
        return self._extract_entries_from_rows(parsed_json)

    def extract_following_from_json(self, file: UploadedFile) -> list[InstagramContact]:
        try:
            parsed_json = json.load(file)
            file.seek(0)
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON file.") from exc

        if not isinstance(parsed_json, dict):
            raise ValueError(
                "Following file must be a JSON object with relationships_following."
            )

        following_rows = parsed_json.get("relationships_following")
        if not isinstance(following_rows, list):
            raise ValueError("Missing or invalid relationships_following array.")
        return self._extract_entries_from_rows(following_rows)

    def _sync_followers_snapshot(
        self, user: User, current_followers: list[InstagramContact]
    ) -> None:
        if current_followers is None:
            raise ValueError("Current followers list is required.")

        with transaction.atomic():
            existing_contacts = {}
            for contact in Contact.objects.all():
                identity_key = self._normalize_identity(
                    link_to_account=contact.link_to_account, username=contact.username
                )
                existing_contacts[identity_key] = contact

            synced_contacts: list[Contact] = []
            seen_identity_keys = set()
            for follower in current_followers:
                identity_key = self._normalize_identity(
                    link_to_account=follower.link_to_account, username=follower.username
                )
                if identity_key in seen_identity_keys:
                    continue
                seen_identity_keys.add(identity_key)

                if identity_key not in existing_contacts:
                    contact = Contact.objects.create(
                        link_to_account=follower.link_to_account,
                        username=follower.username,
                        followed_at=datetime.fromtimestamp(
                            follower.timestamp, tz=timezone.utc
                        ),
                    )
                    existing_contacts[identity_key] = contact
                    synced_contacts.append(contact)
                    continue

                contact = existing_contacts[identity_key]
                updated = False
                if follower.username and contact.username != follower.username:
                    contact.username = follower.username
                    updated = True
                if (
                    follower.link_to_account
                    and contact.link_to_account != follower.link_to_account
                ):
                    contact.link_to_account = follower.link_to_account
                    updated = True
                if updated:
                    contact.save(update_fields=["username", "link_to_account"])
                synced_contacts.append(contact)

            Followers.objects.filter(user=user).delete()

            follower_relations = [
                Followers(
                    user=user,
                    follower=contact,
                )
                for contact in synced_contacts
            ]

            Followers.objects.bulk_create(follower_relations)

    def get_lost_followers(self, user: User, file: UploadedFile):
        current_followers = self.extract_followers_from_json(file)
        db_followers = Contact.objects.filter(followers__user=user).distinct()

        if not db_followers.exists():
            self._sync_followers_snapshot(user=user, current_followers=current_followers)
            return Contact.objects.none(), True

        current_follower_keys = {
            self._normalize_identity(
                link_to_account=follower.link_to_account, username=follower.username
            )
            for follower in current_followers
        }

        lost_followers = [
            contact
            for contact in db_followers
            if self._normalize_identity(
                link_to_account=contact.link_to_account, username=contact.username
            )
            not in current_follower_keys
        ]
        return lost_followers, False

    def override_followers(self, user: User, file: UploadedFile) -> int:
        current_followers = self.extract_followers_from_json(file)
        self._sync_followers_snapshot(user=user, current_followers=current_followers)
        return len(current_followers)

    def get_non_followers(self, user: User, file: UploadedFile):
        following_contacts = self.extract_following_from_json(file)
        follower_contacts = Contact.objects.filter(followers__user=user).distinct()
        follower_keys = {
            self._normalize_identity(
                link_to_account=contact.link_to_account, username=contact.username
            )
            for contact in follower_contacts
        }

        non_followers: list[dict] = []
        seen = set()
        for contact in following_contacts:
            identity_key = self._normalize_identity(
                link_to_account=contact.link_to_account, username=contact.username
            )
            if identity_key in follower_keys or identity_key in seen:
                continue
            seen.add(identity_key)
            non_followers.append(
                {
                    "username": contact.username,
                    "link_to_account": contact.link_to_account,
                    "followed_at": contact.timestamp,
                }
            )
        return non_followers
