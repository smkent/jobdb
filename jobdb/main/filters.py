from decimal import Decimal
from typing import Any

from django.db.models import Q, QuerySet
from django.forms import CharField, HiddenInput
from django_filters import CharFilter, FilterSet  # type: ignore

from .models import Posting


class HiddenCharField(CharField):
    widget = HiddenInput


class HiddenCharFilter(CharFilter):
    field_class = HiddenCharField


class CompanyFilter(FilterSet):
    query = CharFilter(method="universal_search", label="")

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
