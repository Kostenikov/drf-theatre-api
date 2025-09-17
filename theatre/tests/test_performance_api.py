from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from theatre.models import Play, TheatreHall, Performance

PERFORMANCE_URL = reverse("theatre:performance-list")


class PerformanceApiTests(TestCase):
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

        self.hall1 = TheatreHall.objects.create(
            name="Hall 1", rows=5, seats_in_row=10
        )
        self.hall2 = TheatreHall.objects.create(
            name="Hall 2", rows=6, seats_in_row=12
        )

        self.play1 = Play.objects.create(title="Hamlet")
        self.play2 = Play.objects.create(title="Macbeth")

        now = timezone.now()
        self.performance1 = Performance.objects.create(
            play=self.play1, theatre_hall=self.hall1, show_time=now
        )
        self.performance2 = Performance.objects.create(
            play=self.play2,
            theatre_hall=self.hall2,
            show_time=now + timedelta(days=1),
        )

    def test_list_performances_authenticated(self):
        self.client.force_authenticate(self.user)
        res = self.client.get(PERFORMANCE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 2)
        self.assertIn("tickets_available", res.data["results"][0])

    def test_list_performances_as_anonymous(self):
        res = self.client.get(PERFORMANCE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_by_play_title(self):
        self.client.force_authenticate(self.user)
        res = self.client.get(PERFORMANCE_URL, {"play": "Hamlet"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["play"], "Hamlet")

    def test_filter_by_theatre_hall(self):
        self.client.force_authenticate(self.user)
        res = self.client.get(PERFORMANCE_URL, {"theatre_hall": self.hall2.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(
            res.data["results"][0]["theatre_hall"], self.hall2.name
        )

    def test_filter_by_show_date(self):
        self.client.force_authenticate(self.user)
        date_str = self.performance2.show_time.date()
        res = self.client.get(PERFORMANCE_URL, {"show_date": date_str})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["play"], "Macbeth")

    def test_create_performance_as_admin(self):
        self.client.force_authenticate(self.admin)
        payload = {
            "play": self.play1.id,
            "theatre_hall": self.hall1.id,
            "show_time": timezone.now(),
        }
        res = self.client.post(PERFORMANCE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Performance.objects.count(), 3)

    def test_create_performance_as_user(self):
        self.client.force_authenticate(self.user)
        payload = {
            "play": self.play1.id,
            "theatre_hall": self.hall1.id,
            "show_time": timezone.now(),
        }
        res = self.client.post(PERFORMANCE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_performance_as_anonymous(self):
        payload = {
            "play": self.play1.id,
            "theatre_hall": self.hall1.id,
            "show_time": timezone.now(),
        }
        res = self.client.post(PERFORMANCE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
