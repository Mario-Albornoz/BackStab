from django.core.files.base import File

from apps.instagram.serializers import FollowerFileSerializer


class Parser:
    def __init__(self) -> None:
        pass

    def parse_json_followers_file(self, file: File):
        pass

    def parse_json_following_file(self, file: File):
        pass
