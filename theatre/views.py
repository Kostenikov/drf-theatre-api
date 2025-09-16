from django.db.models import Prefetch, F, Count
from django.template.context_processors import request
from rest_framework import viewsets

from theatre.models import (
    Actor,
    Genre,
    Play,
    TheatreHall,
    Performance,
    Reservation,
    Ticket,
)
from theatre.serializers import (
    ActorSerializer,
    GenreSerializer,
    PlaySerializer,
    PlayListSerializer,
    PlayDetailSerializer,
    TheatreHallSerializer,
    PerformanceSerializer,
    PerformanceListSerializer,
    PerformanceDetailSerializer,
    ReservationSerializer,
)


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.prefetch_related("actors", "genres")

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer
        if self.action == "retrieve":
            return PlayDetailSerializer
        return PlaySerializer


class TheatreHallViewSet(viewsets.ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.select_related("play", "theatre_hall")

    def get_queryset(self):
        queryset = self.queryset.all()
        if self.action == "list":
            queryset = queryset.annotate(
                tickets_available=(
                    F("theatre_hall__rows") * F("theatre_hall__seats_in_row")
                    - Count("tickets")
                )
            )
        if self.action == "retrieve":
            queryset = queryset.prefetch_related(
                "tickets", "play__actors", "play__genres"
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer
        if self.action == "retrieve":
            return PerformanceDetailSerializer
        return PerformanceSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.prefetch_related(
        Prefetch(
            "tickets",
            queryset=Ticket.objects.select_related(
                "performance__play", "performance__theatre_hall"
            ).order_by("row", "seat"),
        )
    )
    serializer_class = ReservationSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
