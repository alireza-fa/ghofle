from django.test import SimpleTestCase
from django.urls import reverse, resolve

from apps.accounts.v1.views.profile import ProfileView, ProfileBaseUpdateView


class TestUrls(SimpleTestCase):

    def test_profile(self):
        url = reverse("accounts_v1:profile")
        self.assertEqual(resolve(url).func.view_class, ProfileView)

    def test_profile_update_base(self):
        url = reverse("accounts_v1:profile_update_base")
        self.assertEqual(resolve(url).func.view_class, ProfileBaseUpdateView)
