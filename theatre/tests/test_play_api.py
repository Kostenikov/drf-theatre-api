from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from theatre.models import Play, Actor, Genre


PLAY_URL = reverse("theatre:play-list")


class PlayApiTests(TestCase):
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
        self.actor = Actor.objects.create(first_name="Tom", last_name="Cruise")
        self.genre = Genre.objects.create(name="Action")

    def test_list_plays_as_authenticated(self):
        Play.objects.create(title="Hamlet")
        Play.objects.create(title="King Lear")
        self.client.force_authenticate(self.user)

        res = self.client.get(PLAY_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 2)

    def test_list_plays_as_anonymous(self):
        Play.objects.create(title="Macbeth")
        res = self.client.get(PLAY_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_play_as_admin(self):
        self.client.force_authenticate(self.admin)
        payload = {
            "title": "Mission Impossible",
            "description": "Spy action movie",
            "actors": [self.actor.id],
            "genres": [self.genre.id],
        }
        res = self.client.post(PLAY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        play = Play.objects.get(title="Mission Impossible")
        self.assertIn(self.actor, play.actors.all())
        self.assertIn(self.genre, play.genres.all())

    def test_create_play_as_user(self):
        self.client.force_authenticate(self.user)
        payload = {
            "title": "Top Gun",
            "actors": [self.actor.id],
            "genres": [self.genre.id],
        }
        res = self.client.post(PLAY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
