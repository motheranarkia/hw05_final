from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_pages_access_by_name(self):
        pages = (
            reverse("about:author"),
            reverse("about:tech")
        )
        for page in pages:
            with self.subTest():
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)
