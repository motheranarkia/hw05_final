from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()


class ViewTestClass(TestCase):

    def Setup(self):
        self.user = User.objects.create_user(username='NoName')
        self.authorized_author = Client()
        self.authorized_author.force_login(self.user)

    def test_error_page(self):
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
