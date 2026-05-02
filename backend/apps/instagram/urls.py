from django.urls import path

from apps.instagram.views import LostFollowersView, NonFollowersView, SubmitFollowersView

urlpatterns = [
    path("tracking/lost-followers", LostFollowersView.as_view()),
    path("tracking/followers/submit", SubmitFollowersView.as_view()),
    path("tracking/non-followers", NonFollowersView.as_view()),
]
