from django.db.models import Count, Exists, F, OuterRef, QuerySet, Subquery

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
        qs = qs.order_by("company__name", "title", "url")
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
        .order_by("-count", "name")
    )


def companies_with_postings_count() -> QuerySet:
    return Company.objects.annotate(  # type: ignore
        posting_count=Count("posting")
    )


def user_application_companies(user: User) -> QuerySet:
    return (
        Application.objects.filter(user=user)
        .annotate(company=F("posting__company__name"))
        .values("company")
        .annotate(count=Count("company"))
        .order_by("-count", "company")
    )


def leaderboard_application_companies() -> QuerySet:
    return (
        Application.objects.annotate(company=F("posting__company__name"))
        .values("company")
        .annotate(application_count=Count("pk"))
        .order_by("-application_count", "company")
    )
