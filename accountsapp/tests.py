from django.urls import reverse_lazy
from django.test import TestCase, Client
from django.contrib.auth.models import User
from accountsapp.views import Login


class UnitTestLoginView(TestCase):
    def setUp(self):
        self.login_view = Login()
    
    def test_get_success_url(self):
        expected_url = reverse_lazy('login_done')
        actual_url = self.login_view.get_success_url()
        self.assertEqual(actual_url, expected_url)


class IntegrationTestLoginView(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse_lazy('login_page')
        self.login_done_url = reverse_lazy('login_done')
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_login_success(self):
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'testpassword'})
        self.assertRedirects(response, self.login_done_url)

    def test_get_success_url(self):
        login_view = Login()
        success_url = login_view.get_success_url()
        self.assertEqual(success_url, reverse_lazy('login_done'))




