from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from theatre.models import Actor


ACTOR_URL = reverse("theatre:actor-list")


def detail_url(actor_id):
    return reverse("theatre:actor-detail", args=[actor_id])


class ActorApiTests(TestCase):
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
        self.actor = Actor.objects.create(first_name="Tom", last_name="Hanks")

    def test_list_actors_as_authenticated(self):
        self.client.force_authenticate(self.user)
        res = self.client.get(ACTOR_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(
            res.data["results"][0]["first_name"], self.actor.first_name
        )

    def test_list_actors_as_anonymous(self):
        res = self.client.get(ACTOR_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_actor_as_admin(self):
        self.client.force_authenticate(self.admin)
        payload = {"first_name": "Leonardo", "last_name": "DiCaprio"}
        res = self.client.post(ACTOR_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = Actor.objects.filter(first_name="Leonardo").exists()
        self.assertTrue(exists)

    def test_create_actor_as_user(self):
        self.client.force_authenticate(self.user)
        payload = {"first_name": "Brad", "last_name": "Pitt"}
        res = self.client.post(ACTOR_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
