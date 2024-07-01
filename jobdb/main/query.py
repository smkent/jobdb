from typing import Sequence

from django.db.models import (
    Case,
    Count,
    Exists,
    F,
    FloatField,
    OuterRef,
    QuerySet,
    Subquery,
    When,
)
from django.db.models.aggregates import Sum
from django.db.models.expressions import Value
from django.db.models.functions import Cast, Coalesce, Lower

from .models import Application, Company, Posting, User


def posting_with_applications(
    user: User, queryset: QuerySet | None = None
) -> QuerySet:
    queryset = queryset or Posting.objects.all()
    return queryset.annotate(
        has_application=Exists(
            Application.objects.filter(user=user).filter(
                posting=OuterRef("pk")
            )
        )
    )


def posting_queue_set(user: User, ordered: bool = True) -> QuerySet:
    qs = posting_with_applications(
        user=user, queryset=Posting.objects.filter(closed=None)
    ).filter(has_application=False)
    if ordered:
        qs = qs.order_by("-company__priority", Lower("company__name"), "pk")
    return qs


def posting_queue_companies_count(user: User) -> QuerySet:
    queryset = Company.objects.all()
    assert isinstance(queryset, QuerySet)
    return (
        queryset.annotate(
            count=Subquery(
                posting_queue_set(user)
                .filter(company=OuterRef("pk"))
                .order_by()
                .values("company")
                .annotate(count=Count("pk"))
                .values("count")
            ),
        )
        .filter(count__isnull=False)
        .order_by("-priority", "-count", Lower("name"))
    )


def companies_with_counts() -> QuerySet:
    queryset = Company.objects.all().annotate(
        posting_count=Count("posting"),
        apps_count=Coalesce(
            Subquery(
                Application.objects.filter(posting__company=OuterRef("pk"))
                .values("posting__company")
                .annotate(count=Count("pk"))
                .values("count"),
            ),
            0,
        ),
    )
    assert isinstance(queryset, QuerySet)
    return queryset


def companies_completion_stats(
    order_by: Sequence[str] | None = None,
) -> QuerySet:
    order_by = order_by or ["-queue_count"]
    queryset = (
        companies_with_counts()
        .annotate(
            queue_count=Coalesce(
                Subquery(
                    Posting.objects.filter(closed=None)
                    .annotate(
                        queue_count=Value(
                            Application.objects.values("user")
                            .distinct()
                            .count()
                        )
                        - Subquery(
                            Application.objects.filter(posting=OuterRef("pk"))
                            .values("posting")
                            .annotate(count=Count("pk"))
                            .values("count")
                        )
                    )
                    .filter(company=OuterRef("pk"))
                    .values("company")
                    .annotate(sum=Sum("queue_count"))
                    .values("sum"),
                ),
                0,
            ),
            max_apps=F("queue_count") + F("apps_count"),
            apps_percent=(
                Case(
                    When(max_apps=0, then=Value(0.0)),
                    default=(
                        Cast(F("apps_count"), FloatField())
                        / Cast(F("max_apps"), FloatField())
                    ),
                )
            ),
        )
        .order_by(*order_by)
    )
    assert isinstance(queryset, QuerySet)
    return queryset


def user_application_companies(user: User) -> QuerySet:
    queryset = Company.objects.all()
    assert isinstance(queryset, QuerySet)
    return (
        queryset.annotate(
            count=Subquery(
                posting_with_applications(user)
                .filter(has_application=True)
                .filter(company=OuterRef("pk"))
                .order_by()
                .values("company")
                .annotate(count=Count("pk"))
                .values("count")
            ),
        )
        .filter(count__isnull=False)
        .order_by("-count", Lower("name"))
    )


def leaderboard_application_companies() -> QuerySet:
    return (
        Application.objects.annotate(company=F("posting__company__name"))
        .values("company")
        .annotate(application_count=Count("pk"))
        .order_by("-application_count", "company")
    )
