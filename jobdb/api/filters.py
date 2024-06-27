from django.db.models import QuerySet
from django_filters import BooleanFilter, CharFilter, FilterSet  # type: ignore

from ..main.models import Application, Company, Posting


class CompanyFilter(FilterSet):
    class Meta:
        model = Company
        fields = ["name"]


class PostingFilter(FilterSet):
    company = CharFilter(
        field_name="company__name", lookup_expr="iexact", label=""
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
