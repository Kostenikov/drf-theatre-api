from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from theatre.models import TheatreHall

THEATRE_HALL_URL = reverse("theatre:theatrehall-list")


class TheatreHallApiTests(TestCase):
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
        self.hall = TheatreHall.objects.create(
            name="Main Hall", rows=10, seats_in_row=15
        )

    def test_list_theatre_halls_as_authenticated(self):
        self.client.force_authenticate(self.user)
        res = self.client.get(THEATRE_HALL_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["name"], self.hall.name)

    def test_list_theatre_halls_as_anonymous(self):
        res = self.client.get(THEATRE_HALL_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_theatre_hall_as_admin(self):
        self.client.force_authenticate(self.admin)
        payload = {"name": "Secondary Hall", "rows": 5, "seats_in_row": 20}
        res = self.client.post(THEATRE_HALL_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        hall = TheatreHall.objects.get(name="Secondary Hall")
        self.assertEqual(hall.rows, 5)
        self.assertEqual(hall.seats_in_row, 20)

    def test_create_theatre_hall_as_user(self):
        self.client.force_authenticate(self.user)
        payload = {"name": "I'm TIRED", "rows": 5, "seats_in_row": 20}
        res = self.client.post(THEATRE_HALL_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
