from django_filters import (
    rest_framework as filters,
    BaseInFilter,
    NumberFilter,
)

from theatre.models import Performance, Play


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class PerformanceFilter(filters.FilterSet):
    play = filters.CharFilter(
        field_name="play__title",
        lookup_expr="icontains",
        help_text="search by play title [ex. 'Hamlet']",
    )
    theatre_hall = filters.NumberFilter(
        field_name="theatre_hall__id",
        lookup_expr="exact",
        help_text="search by theatre hall id [ex. '1' or '2']",
    )
    show_date = filters.DateTimeFilter(
        field_name="show_time",
        lookup_expr="date",
        help_text="search by date [ex. '2025-09-16']",
    )

    class Meta:
        model = Performance
        fields = ["play", "theatre_hall"]


class PlayFilter(filters.FilterSet):
    title = filters.CharFilter(
        field_name="title",
        lookup_expr="icontains",
        help_text="search by title [ex. 'Hamlet']",
    )
    actors = NumberInFilter(
        field_name="actors__id",
        lookup_expr="in",
        distinct=True,
        help_text="search by actor id [ex. '1' or '2']",
    )
    genres = NumberInFilter(
        field_name="genres__id",
        lookup_expr="in",
        distinct=True,
        help_text="search by genre id [ex. '1' or '2']",
    )

    class Meta:
        model = Play
        fields = ["title", "actors", "genres"]
