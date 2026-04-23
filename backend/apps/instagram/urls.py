from django.urls import path

from apps.instagram.views import LostFollowersViewSet

urlpatterns = [
    path("tracking/lost-followers", LostFollowersViewSet.as_view()),
]
