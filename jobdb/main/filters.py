from decimal import Decimal
from typing import Any

import django_filters  # type: ignore
from django.db.models import Q, QuerySet

from .models import Company


class CompanyFilter(django_filters.FilterSet):
    query = django_filters.CharFilter(method="universal_search", label="")

    class Meta:
        model = Company
        fields = ["query"]

    def universal_search(
        self, queryset: QuerySet, name: str, value: Any
    ) -> QuerySet:
        if value.replace(".", "", 1).isdigit():
            value = Decimal(value)
            return queryset.filter(Q(pk=value))
        return queryset.filter(Q(name__icontains=value))
