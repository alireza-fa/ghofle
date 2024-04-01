from django.urls import path

from apps.accounts.api.http.v1.views import profile


urlpatterns = [
    path("profile/", profile.ProfileView.as_view()),
]
