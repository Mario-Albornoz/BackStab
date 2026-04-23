import json

from django.core.files.uploadedfile import UploadedFile
from rest_framework import serializers

from apps.instagram.models import Contact, Followers, Following


class ContactSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"


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
            raise ValueError("Invalid Json File", exc)

        if not isinstance(parsed_json, list):
            raise ValueError("Expeted top-level JSON array")
        return value


class FollowerFileSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value: UploadedFile):
        if not value.name.endswith(".json"):
            raise serializers.ValidationError(
                "File Uploaded format is not Allowed, Only .json files are allowed."
            )
        return value


class FollowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Following
        fields = "__all__"


class FollowersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Followers
        fields = "__all__"
