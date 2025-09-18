from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone

from theatre.models import Play, TheatreHall, Performance, Reservation, Ticket

RESERVATION_URL = reverse("theatre:reservation-list")


class ReservationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="user@test.com",
            email="user@test.com",
            password="password",
        )
        self.user2 = get_user_model().objects.create_user(
            username="user2@test.com",
            email="user2@test.com",
            password="password",
        )
        self.admin = get_user_model().objects.create_superuser(
            username="admin@test.com",
            email="admin@test.com",
            password="password",
        )

        self.hall = TheatreHall.objects.create(
            name="Main Hall", rows=5, seats_in_row=10
        )
        self.play = Play.objects.create(title="Hamlet")
        self.performance = Performance.objects.create(
            play=self.play, theatre_hall=self.hall, show_time=timezone.now()
        )

    def test_list_reservations_authenticated_user_sees_only_own(self):
        res1 = Reservation.objects.create(user=self.user)
        Ticket.objects.create(
            reservation=res1, performance=self.performance, row=1, seat=1
        )
        res2 = Reservation.objects.create(user=self.user2)
        Ticket.objects.create(
            reservation=res2, performance=self.performance, row=1, seat=2
        )

        self.client.force_authenticate(self.user)
        res = self.client.get(RESERVATION_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["tickets"][0]["row"], 1)
        self.assertEqual(res.data["results"][0]["tickets"][0]["seat"], 1)

    def test_list_reservations_as_anonymous(self):
        res = self.client.get(RESERVATION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_reservation_valid_tickets(self):
        self.client.force_authenticate(self.user)
        payload = {
            "tickets": [
                {"performance": self.performance.id, "row": 1, "seat": 1},
                {"performance": self.performance.id, "row": 1, "seat": 2},
            ]
        }
        res = self.client.post(RESERVATION_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reservation.objects.count(), 1)
        self.assertEqual(Ticket.objects.count(), 2)

    def test_create_reservation_invalid_row_seat(self):
        self.client.force_authenticate(self.user)
        payload = {
            "tickets": [
                {"performance": self.performance.id, "row": 0, "seat": 1}
            ]
        }
        res = self.client.post(RESERVATION_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("row", str(res.data))

        payload = {
            "tickets": [
                {"performance": self.performance.id, "row": 1, "seat": 20}
            ]
        }
        res = self.client.post(RESERVATION_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("seat", str(res.data))

    def test_create_reservation_as_anonymous(self):
        payload = {
            "tickets": [
                {"performance": self.performance.id, "row": 1, "seat": 1}
            ]
        }
        res = self.client.post(RESERVATION_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_reservation_without_tickets(self):
        self.client.force_authenticate(self.user)
        payload = {}
        res = self.client.post(RESERVATION_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
