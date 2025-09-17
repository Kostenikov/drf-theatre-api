from django.db.models import Prefetch, F, Count
from django_filters import rest_framework
from rest_framework import filters
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from theatre.filters import PerformanceFilter, PlayFilter
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
    ReservationListSerializer,
)


@extend_schema(tags=["actor"])
class ActorViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


@extend_schema(tags=["genre"])
class GenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


@extend_schema(tags=["play"])
class PlayViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    filterset_class = PlayFilter
    filter_backends = (
        filters.OrderingFilter,
        rest_framework.DjangoFilterBackend,
    )
    ordering_fields = ["title"]
    ordering = ["title"]
    queryset = Play.objects.prefetch_related("actors", "genres")

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer
        if self.action == "retrieve":
            return PlayDetailSerializer
        return PlaySerializer


@extend_schema(tags=["theatre_hall"])
class TheatreHallViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer


@extend_schema(tags=["performance"])
class PerformanceViewSet(viewsets.ModelViewSet):
    filterset_class = PerformanceFilter
    filter_backends = (
        filters.OrderingFilter,
        rest_framework.DjangoFilterBackend,
    )
    ordering_fields = ["show_time", "play__title"]
    ordering = ["-show_time", "play__title"]
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


@extend_schema(tags=["reservation"])
class ReservationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Reservation.objects.prefetch_related(
        Prefetch(
            "tickets",
            queryset=Ticket.objects.select_related(
                "performance__play", "performance__theatre_hall"
            ).order_by("row", "seat"),
        )
    )
    serializer_class = ReservationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        return ReservationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
