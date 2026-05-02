from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response

from apps.instagram.serializers import (
    ContactSerializer,
    FollowerFileSerializer,
    FollowingFileSerializer,
)
from apps.instagram.services import LostFollowersService


class LostFollowersView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FollowerFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lost_followers_service = LostFollowersService()
        file = serializer.validated_data["file"]

        try:
            lost_followers, initialized = lost_followers_service.get_lost_followers(
                file=file, user=request.user
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "lost_followers": ContactSerializer(lost_followers, many=True).data,
                "baseline_initialized": initialized,
            },
            status=status.HTTP_200_OK,
        )


class SubmitFollowersView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FollowerFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data["file"]

        lost_followers_service = LostFollowersService()
        try:
            total_followers = lost_followers_service.override_followers(
                user=request.user, file=file
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"detail": "Followers snapshot updated.", "total_followers": total_followers},
            status=status.HTTP_200_OK,
        )


class NonFollowersView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FollowingFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data["file"]

        lost_followers_service = LostFollowersService()
        try:
            non_followers = lost_followers_service.get_non_followers(
                user=request.user, file=file
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"non_followers": non_followers}, status=status.HTTP_200_OK)
