from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response

from apps.instagram.models import Contact
from apps.instagram.serializers import ContactSerilizer, FollowerFileSerializer
from apps.instagram.services import LostFollowersService


class LostFollowersView(APIView):

    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        update_followers: bool = request.headers.get("update_followers")
        serializer = FollowerFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lost_followers_service = LostFollowersService()

        file = serializer.validated_data["file"]

        try:
            lost_followers = lost_followers_service.get_lost_followers(
                file=file, user=request.user
            )

            if update_followers:

                pass

        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"lost_followers": ContactSerilizer(lost_followers, many=True)},
            status=status.HTTP_200_OK,
        )

    def submit_new_follower_list(self, request):
        serializer = FollowerFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
