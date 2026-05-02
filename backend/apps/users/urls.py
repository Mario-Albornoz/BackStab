from apps.users.views import SignupView
from django.urls import path

urlpatterns = [
    path("signup/", SignupView.as_view()),
]
