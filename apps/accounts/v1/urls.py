from django.urls import path

from apps.accounts.v1.views import profile

urlpatterns = [
    path("profile/", profile.ProfileView.as_view()),
    path("profile/update/base/", profile.ProfileBaseUpdateView.as_view()),
]
