from django.test import TestCase

from rest_framework.test import APITestCase


class RndTests(APITestCase):

    def test_basic(self):
        response = self.client.get('/data/rnd/wcdma/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
