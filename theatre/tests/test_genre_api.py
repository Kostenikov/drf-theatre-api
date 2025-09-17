from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from theatre.models import Genre


GENRE_URL = reverse("theatre:genre-list")


class GenreApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="user@test.com",
            email="user@test.com",
            password="password",
        )
        self.admin = get_user_model().objects.create_superuser(
            username="admin@test.com",
            email="admin@test.com",
            password="password",
        )

    def test_list_genres_as_authenticated(self):
        Genre.objects.create(name="Drama")
        Genre.objects.create(name="Horror")
        self.client.force_authenticate(self.user)

        res = self.client.get(GENRE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 2)

    def test_list_genres_as_anonymous(self):
        Genre.objects.create(name="Comedy")
        res = self.client.get(GENRE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_genre_as_admin(self):
        self.client.force_authenticate(self.admin)
        payload = {"name": "Comedy"}
        res = self.client.post(GENRE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = Genre.objects.filter(name="Comedy").exists()
        self.assertTrue(exists)

    def test_create_genre_as_user(self):
        self.client.force_authenticate(self.user)
        payload = {"name": "Thriller"}
        res = self.client.post(GENRE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
