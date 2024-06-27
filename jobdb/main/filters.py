from decimal import Decimal
from typing import Any

from django.db.models import Q, QuerySet
from django.forms import CharField, HiddenInput
from django_filters import BooleanFilter, CharFilter, FilterSet  # type: ignore

from .models import Application, Company, Posting


class HiddenCharField(CharField):
    widget = HiddenInput


class HiddenCharFilter(CharFilter):
    field_class = HiddenCharField


class CompanyFilter(FilterSet):
    query = CharFilter(method="universal_search", label="")

    class Meta:
        model = Company
        fields = ["query"]

    def universal_search(
        self, queryset: QuerySet, name: str, value: Any
    ) -> QuerySet:
        if value.replace(".", "", 1).isdigit():
            value = Decimal(value)
            return queryset.filter(Q(pk=value))
        condition = Q()
        for field in ["name", "url", "notes"]:
            condition.add(Q(**{f"{field}__icontains": value}), Q.OR)
        return queryset.filter(condition)


class PostingFilter(FilterSet):
    query = CharFilter(method="universal_search", label="")
    company = HiddenCharFilter(
        field_name="company__name", lookup_expr="iexact", label=""
    )

    class Meta:
        model = Posting
        fields = ["query"]

    def universal_search(
        self, queryset: QuerySet, name: str, value: Any
    ) -> QuerySet:
        if value.replace(".", "", 1).isdigit():
            value = Decimal(value)
            return queryset.filter(Q(pk=value))
        condition = Q()
        for field in ["company__name", "url", "notes"]:
            condition.add(Q(**{f"{field}__icontains": value}), Q.OR)
        return queryset.filter(condition)


class ApplicationFilter(FilterSet):
    query = CharFilter(method="universal_search", label="")
    company = HiddenCharFilter(
        field_name="posting__company__name", lookup_expr="iexact", label=""
    )
    reported = BooleanFilter(
        field_name="reported",
        method="filter_reported",
        label="Reported",
    )

    class Meta:
        model = Application
        fields = ["query"]

    def universal_search(
        self, queryset: QuerySet, name: str, value: Any
    ) -> QuerySet:
        if value.replace(".", "", 1).isdigit():
            value = Decimal(value)
            return queryset.filter(Q(pk=value))
        condition = Q()
        for field in ["posting__company__name", "posting__url", "notes"]:
            condition.add(Q(**{f"{field}__icontains": value}), Q.OR)
        return queryset.filter(condition)

    def filter_reported(
        self, queryset: QuerySet, name: str, value: bool
    ) -> QuerySet:
        return queryset.filter(reported__isnull=(not value))
