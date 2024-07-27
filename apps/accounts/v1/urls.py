from django.urls import path

from apps.accounts.v1.views import profile


app_name = "accounts_v1"

urlpatterns = [
    path("profile/", profile.ProfileView.as_view(), name="profile"),
    path("profile/update/base/", profile.ProfileBaseUpdateView.as_view(), name="profile_update_base"),
    path("profile/update/avatar-image/", profile.ProfileUpdateAvatarImageView.as_view(), name="profile-update-avatar-image"),
]
