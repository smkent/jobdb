from django.db.models import QuerySet
from django_filters import (  # type: ignore
    BooleanFilter,
    CharFilter,
    ChoiceFilter,
    FilterSet,
    OrderingFilter,
)

from ..main.models import Application, Company, Posting, Priority


class CompanyFilter(FilterSet):
    o = OrderingFilter(
        fields=(
            ("name", "name"),
            ("posting_count", "num_postings"),
        )
    )

    class Meta:
        model = Company
        fields = ["name"]


class PostingFilter(FilterSet):
    company = CharFilter(
        field_name="company__name", lookup_expr="iexact", label=""
    )
    in_wa = BooleanFilter(field_name="in_wa", label="In WA")
    priority = ChoiceFilter(
        choices=Priority.choices,
        field_name="company__priority",
        label="Priority",
    )

    class Meta:
        model = Posting
        fields = ["company"]


class ApplicationFilter(FilterSet):
    company = CharFilter(
        field_name="posting__company__name", lookup_expr="iexact", label=""
    )
    reported = BooleanFilter(
        field_name="reported",
        method="filter_reported",
        label="Reported",
    )

    class Meta:
        model = Application
        fields = ["company", "reported", "bona_fide"]

    def filter_reported(
        self, queryset: QuerySet, name: str, value: bool
    ) -> QuerySet:
        return queryset.filter(reported__isnull=(not value))
