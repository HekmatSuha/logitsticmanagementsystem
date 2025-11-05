from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CoreAccessControlTests(TestCase):
    def setUp(self):
        self.username = "core-user"
        self.password = "test-pass"
        get_user_model().objects.create_user(
            username=self.username, password=self.password
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('dashboard')}",
        )

    def test_dashboard_allows_authenticated_user(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_global_search_requires_login(self):
        response = self.client.get(reverse("global_search"))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('global_search')}",
        )

    def test_global_search_allows_authenticated_user(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse("global_search"))
        self.assertEqual(response.status_code, 200)
