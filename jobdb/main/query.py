from django.db.models import (
    Count,
    Exists,
    F,
    OuterRef,
    Q,
    QuerySet,
    Subquery,
    Window,
)
from django.db.models.functions import Coalesce, Lower, RowNumber

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


def company_posting_queue_set(user: User) -> QuerySet:
    base_qs = posting_with_applications(user)
    windowed_qs = (
        base_qs.filter(
            Q(has_application=True)
            | (Q(has_application=False) & Q(closed=None))
        )
        .annotate(
            row_number=Window(
                expression=RowNumber(),
                partition_by=[F("company")],
                order_by=["-has_application", "-in_wa", "-created"],
            )
        )
        .order_by("row_number")
        .filter(row_number__lte=2)
    )
    qs = base_qs.filter(
        pk__in=Subquery(windowed_qs.values("pk")), has_application=False
    )
    return qs.order_by(
        "-company__priority", Lower("company__name"), "-in_wa", "pk"
    )


def posting_queue_companies_count(user: User) -> QuerySet:
    queryset = Company.objects.all()
    assert isinstance(queryset, QuerySet)
    return (
        queryset.annotate(
            count=Coalesce(
                Subquery(
                    company_posting_queue_set(user)
                    .filter(company=OuterRef("pk"))
                    .order_by()
                    .values("company")
                    .annotate(count=Count("pk"))
                    .values("count")
                ),
                0,
            ),
            count_in_wa=Coalesce(
                Subquery(
                    company_posting_queue_set(user)
                    .filter(in_wa=True)
                    .filter(company=OuterRef("pk"))
                    .order_by()
                    .values("company")
                    .annotate(count=Count("pk"))
                    .values("count")
                ),
                0,
            ),
        )
        .filter(count__gt=0)
        .order_by("-priority", "-count", Lower("name"))
    )


def companies_with_posting_counts() -> QuerySet:
    queryset = Company.objects.all().annotate(
        posting_count=Count("posting"),
        open_posting_count=Coalesce(
            Subquery(
                Posting.objects.filter(closed=None)
                .filter(company=OuterRef("pk"))
                .values("company")
                .annotate(count=Count("pk"))
                .values("count")
            ),
            0,
        ),
    )
    assert isinstance(queryset, QuerySet)
    return queryset


def companies_with_counts() -> QuerySet:
    queryset = companies_with_posting_counts().annotate(
        apps_count=Coalesce(
            Subquery(
                Application.objects.filter(posting__company=OuterRef("pk"))
                .values("posting__company")
                .annotate(count=Count("pk"))
                .values("count"),
            ),
            0,
        ),
        reported_apps_count=Coalesce(
            Subquery(
                Application.objects.filter(reported__isnull=False)
                .filter(posting__company=OuterRef("pk"))
                .values("posting__company")
                .annotate(count=Count("pk"))
                .values("count"),
            ),
            0,
        ),
        available_count=F("open_posting_count") + F("apps_count"),
    )
    assert isinstance(queryset, QuerySet)
    return queryset


def user_application_companies(user: User) -> QuerySet:
    queryset = Company.objects.all()
    assert isinstance(queryset, QuerySet)
    return (
        queryset.annotate(
            count=Coalesce(
                Subquery(
                    posting_with_applications(user)
                    .filter(has_application=True)
                    .filter(company=OuterRef("pk"))
                    .order_by()
                    .values("company")
                    .annotate(count=Count("pk"))
                    .values("count")
                ),
                0,
            ),
            count_in_wa=Coalesce(
                Subquery(
                    posting_with_applications(user)
                    .filter(in_wa=True)
                    .filter(has_application=True)
                    .filter(company=OuterRef("pk"))
                    .order_by()
                    .values("company")
                    .annotate(count=Count("pk"))
                    .values("count")
                ),
                0,
            ),
        )
        .filter(count__gt=0)
        .order_by("-count", Lower("name"))
    )


def user_companies_leaderboard() -> QuerySet:
    return (
        Application.objects.values("user__username", "user__first_name")
        .annotate(count=Count("posting__company", distinct=True))
        .order_by("-count", "user__username")
    )
