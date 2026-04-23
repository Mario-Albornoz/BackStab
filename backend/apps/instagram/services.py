import json
from dataclasses import dataclass

from apps.instagram.models import Contact, Followers
from apps.instagram.serializers import FollowerFileSerializer
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction


@dataclass
class Follower:
    link_to_follower: str
    username: str
    timestamp: str


class LostFollowersService:
    def __init__(self) -> None:
        self.current_follwers: list[Follower]
        pass

    def extract_followers_from_json(self, file: UploadedFile) -> list[Follower]:
        try:
            parsed_json = json.load(file)
            file.seek(0)
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid Json File", exc)

        if not isinstance(parsed_json, list):
            raise ValueError("Expeted top-level JSON array")

        serializer = FollowerFileSerializer(data=parsed_json, many=True)
        serializer.is_valid(raise_exception=True)

        followers: list[Follower] = []

        for item in serializer.validated_data:
            for occurance in item["string_list_data"]:
                follower = Follower(
                    link_to_follower=occurance["href"],
                    username=occurance["value"],
                    timestamp=occurance["timestamp"],
                )
                followers.append(follower)
        return followers

    def get_lost_followers(self, user, file: UploadedFile):
        self.current_followers: list[Follower] = self.extract_followers_from_json(file)

        current_followers_usernames = {
            follower.username for follower in self.current_followers
        }

        db_followers = Contact.objects.filter(followers__user=user).distinct()

        lost_followers = db_followers.exclude(username__in=current_followers_usernames)

        return lost_followers

    def override_followers(self, user):
        if not hasattr(self, "current_followers") or self.current_followers is None:
            raise ValueError("current_followers has not been defined")

        with transaction.atomic():
            current_usernames = [f.username for f in self.current_followers]

            existing_contacts = {
                contact.username: contact
                for contact in Contact.objects.filter(username__in=current_usernames)
            }

            contacts_to_create: list[Contact] = []
            for follower in self.current_followers:
                if follower.username not in existing_contacts:
                    contacts_to_create.append(
                        Contact(
                            link_to_account=follower.link_to_follower,
                            username=follower.username,
                            followed_at=follower.timestamp,
                        )
                    )

            created_contacts = Contact.objects.bulk_create(contacts_to_create)

            for contact in created_contacts:
                existing_contacts[contact.username] = contact

            Followers.objects.filter(user=user).delete()

            follower_relations = [
                Followers(user=user, contact=existing_contacts[follower.username])
                for follower in self.current_followers
            ]

            Followers.objects.bulk_create(follower_relations)
