from decimal import Decimal
from typing import Any

from crispy_bootstrap5.bootstrap5 import FloatingField  # type: ignore
from crispy_forms.helper import FormHelper  # type: ignore
from crispy_forms.layout import Column, Layout, Row, Submit  # type: ignore
from django.db.models import Q, QuerySet
from django.forms import CharField, Form, HiddenInput
from django_filters import BooleanFilter, CharFilter  # type: ignore
from django_filters import FilterSet as BaseFilterSet

from .models import Application, Company, Posting


class HiddenCharField(CharField):
    widget = HiddenInput


class HiddenCharFilter(CharFilter):
    field_class = HiddenCharField


class FilterSet(BaseFilterSet):
    def get_form_class(self) -> type[Form]:
        base_form_class = super().get_form_class()

        class FormClass(base_form_class):  # type: ignore
            def __init__(self, *args: Any, **kwargs: Any):
                super().__init__(*args, **kwargs)
                self.helper = FormHelper(self)
                layout_items = []
                for field_name in self.fields.keys():
                    layout_items.append(
                        Column(FloatingField(field_name), css_class="col-auto")
                    )
                layout_items.append(
                    Column(
                        Submit("submit", "Filter", css_class="col-auto p-3")
                    )
                )
                self.helper.layout = Layout(Row(*layout_items))

        return FormClass


class CompanyFilter(FilterSet):
    query = CharFilter(method="universal_search", label="Search")
    available = BooleanFilter(
        field_name="available", method="filter_available", label="Available"
    )
    wa_available = BooleanFilter(
        field_name="wa_available",
        method="filter_wa_available",
        label="WA Available",
    )
    filed = BooleanFilter(
        field_name="filed", method="filter_filed", label="Filed"
    )

    class Meta:
        model = Company
        fields = ["query"]

    def universal_search(
        self, queryset: QuerySet, name: str, value: Any
    ) -> QuerySet:
        condition = Q()
        if value.replace(".", "", 1).isdigit():
            condition.add(Q(**{"pk": Decimal(value)}), Q.OR)
        for field in ["name", "url", "notes"]:
            condition.add(Q(**{f"{field}__icontains": value}), Q.OR)
        return queryset.filter(condition)

    def filter_available(
        self, queryset: QuerySet, name: str, value: bool
    ) -> QuerySet:
        if value:
            return queryset.filter(available_count__gt=0)
        return queryset.filter(available_count=0)

    def filter_filed(
        self, queryset: QuerySet, name: str, value: bool
    ) -> QuerySet:
        if value:
            return queryset.filter(filed__isnull=False)
        return queryset.filter(filed=None)

    def filter_wa_available(
        self, queryset: QuerySet, name: str, value: bool
    ) -> QuerySet:
        if value:
            return queryset.filter(wa_available_count__gt=0)
        return queryset.filter(wa_available_count=0)


class PostingFilter(FilterSet):
    query = CharFilter(method="universal_search", label="Search")
    company = HiddenCharFilter(
        field_name="company__name", lookup_expr="iexact", label=""
    )
    in_wa = BooleanFilter(
        field_name="in_wa", method="filter_in_wa", label="In WA"
    )

    class Meta:
        model = Posting
        fields = ["query"]

    def universal_search(
        self, queryset: QuerySet, name: str, value: Any
    ) -> QuerySet:
        condition = Q()
        if value.replace(".", "", 1).isdigit():
            condition.add(Q(**{"pk": Decimal(value)}), Q.OR)
        for field in ["company__name", "url", "notes"]:
            condition.add(Q(**{f"{field}__icontains": value}), Q.OR)
        return queryset.filter(condition)

    def filter_in_wa(
        self, queryset: QuerySet, name: str, value: bool
    ) -> QuerySet:
        return queryset.filter(in_wa=value)


class AllPostingFilter(PostingFilter):
    is_open = BooleanFilter(
        field_name="closed", method="filter_open", label="Open"
    )

    class Meta:
        model = Posting
        fields = ["query"]

    def filter_open(
        self, queryset: QuerySet, name: str, value: bool
    ) -> QuerySet:
        return queryset.filter(closed__isnull=value)


class ApplicationFilter(FilterSet):
    query = CharFilter(method="universal_search", label="Search")
    company = HiddenCharFilter(
        field_name="posting__company__name", lookup_expr="iexact", label=""
    )
    in_wa = BooleanFilter(
        field_name="in_wa", method="filter_in_wa", label="In WA"
    )
    reported = BooleanFilter(
        field_name="reported", method="filter_reported", label="Reported"
    )

    class Meta:
        model = Application
        fields = ["query"]

    def universal_search(
        self, queryset: QuerySet, name: str, value: Any
    ) -> QuerySet:
        condition = Q()
        if value.replace(".", "", 1).isdigit():
            condition.add(Q(**{"pk": Decimal(value)}), Q.OR)
        for field in ["posting__company__name", "posting__url", "notes"]:
            condition.add(Q(**{f"{field}__icontains": str(value)}), Q.OR)
        return queryset.filter(condition)

    def filter_in_wa(
        self, queryset: QuerySet, name: str, value: bool
    ) -> QuerySet:
        return queryset.filter(posting__in_wa=value)

    def filter_reported(
        self, queryset: QuerySet, name: str, value: bool
    ) -> QuerySet:
        return queryset.filter(reported__isnull=(not value))
