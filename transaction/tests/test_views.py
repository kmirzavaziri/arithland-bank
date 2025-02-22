from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class LoginViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test_user", password="password")
        self.login_url = reverse("login")
        self.dashboard_url = reverse("dashboard")

    def test_login_valid_credentials(self):
        response = self.client.post(self.login_url, {"username": "test_user", "password": "password"})
        self.assertRedirects(response, self.dashboard_url)

    def test_login_invalid_credentials(self):
        response = self.client.post(self.login_url, {"username": "test_user", "password": "wrong"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "form.html")

    def test_login_authenticated_user_redirects(self):
        self.client.login(username="test_user", password="password")
        response = self.client.get(self.login_url)
        self.assertRedirects(response, self.dashboard_url)


class LogoutViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test_user", password="password")
        self.login_url = reverse("login")
        self.dashboard_url = reverse("dashboard")
        self.logout_url = reverse("logout")

    def test_logout_authenticated_user(self):
        self.client.login(username="test_user", password="password")
        response = self.client.post(self.logout_url)
        self.assertRedirects(response, self.login_url)


class DashboardViewTestCase(TestCase):
    pass


class TeamsViewTestCase(TestCase):
    pass


class TransactionsViewTestCase(TestCase):
    pass


class GetUserDetailsAPIViewTestCase(TestCase):
    pass


class TeamsGetBalanceByNumberAPIViewTestCase(TestCase):
    pass


class SetUserCompetitionAPIViewTestCase(TestCase):
    pass
