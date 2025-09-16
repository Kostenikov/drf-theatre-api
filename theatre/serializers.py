from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from theatre.models import (
    Actor,
    Genre,
    Play,
    TheatreHall,
    Performance,
    Ticket,
    Reservation,
)


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ("id", "first_name", "last_name")


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name")


class PlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = ("id", "title", "description", "actors", "genres")


class PlayListSerializer(PlaySerializer):
    actors = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="full_name",
    )
    genres = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name",
    )


class PlayDetailSerializer(PlaySerializer):
    actors = ActorSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)


class TheatreHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreHall
        fields = ("id", "name", "rows", "seats_in_row", "capacity")


class PerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance
        fields = ("id", "show_time", "play", "theatre_hall")


class PerformanceListSerializer(PerformanceSerializer):
    play = serializers.SlugRelatedField(
        read_only=True,
        slug_field="title",
    )
    theatre_hall = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name",
    )
    theatre_hall_capacity = serializers.IntegerField(
        read_only=True,
        source="theatre_hall.capacity",
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Performance
        fields = (
            "id",
            "show_time",
            "play",
            "theatre_hall",
            "theatre_hall_capacity",
            "tickets_available",
        )


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance")

    def validate(self, attrs):
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["performance"].theatre_hall,
            ValidationError,
        )


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class PerformanceDetailSerializer(PerformanceSerializer):
    play = PlayDetailSerializer(read_only=True)
    theatre_hall = TheatreHallSerializer(read_only=True)
    taken_places = TicketSeatsSerializer(
        many=True,
        read_only=True,
        source="tickets",
    )

    class Meta:
        model = Performance
        fields = ("id", "show_time", "play", "theatre_hall", "taken_places")


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Reservation
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            reservation = Reservation.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)
            return reservation
