import json

from django.core.files.uploadedfile import UploadedFile
from rest_framework import serializers

from apps.instagram.models import Contact, Followers, Following


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"


class _InstagramStringEntrySerializer(serializers.Serializer):
    href = serializers.CharField()
    value = serializers.CharField()
    timestamp = serializers.IntegerField()


class _InstagramListItemSerializer(serializers.Serializer):
    string_list_data = _InstagramStringEntrySerializer(many=True)


class FollowingFileSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value: UploadedFile):
        if not value.name.endswith(".json"):
            raise serializers.ValidationError(
                "File Uploaded format is not Allowed, Only .json files are allowed."
            )
        try:
            parsed_json = json.load(value)
            value.seek(0)
        except json.JSONDecodeError as exc:
            raise serializers.ValidationError("Invalid JSON file.") from exc

        if not isinstance(parsed_json, dict):
            raise serializers.ValidationError(
                "Following file must be a JSON object with relationships_following."
            )

        following_rows = parsed_json.get("relationships_following")
        if not isinstance(following_rows, list):
            raise serializers.ValidationError(
                "Missing or invalid relationships_following array."
            )

        nested_serializer = _InstagramListItemSerializer(data=following_rows, many=True)
        nested_serializer.is_valid(raise_exception=True)
        return value


class FollowerFileSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value: UploadedFile):
        if not value.name.endswith(".json"):
            raise serializers.ValidationError(
                "File Uploaded format is not Allowed, Only .json files are allowed."
            )
        try:
            parsed_json = json.load(value)
            value.seek(0)
        except json.JSONDecodeError as exc:
            raise serializers.ValidationError("Invalid JSON file.") from exc

        if not isinstance(parsed_json, list):
            raise serializers.ValidationError("Followers file must be a JSON array.")

        nested_serializer = _InstagramListItemSerializer(data=parsed_json, many=True)
        nested_serializer.is_valid(raise_exception=True)
        return value


class FollowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Following
        fields = "__all__"


class FollowersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Followers
        fields = "__all__"
