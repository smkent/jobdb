from django.db.models import Count, Exists, OuterRef, QuerySet, Subquery
from django.db.models.functions import Coalesce, Lower

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
            count_in_wa=Subquery(
                posting_queue_set(user)
                .filter(in_wa=True)
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
            count_in_wa=Subquery(
                posting_with_applications(user)
                .filter(in_wa=True)
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


def user_companies_leaderboard() -> QuerySet:
    return (
        Application.objects.values("user__username", "user__first_name")
        .annotate(count=Count("posting__company", distinct=True))
        .order_by("-count", "user__username")
    )
