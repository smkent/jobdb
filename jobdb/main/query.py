from django.db.models import Case, Count, F, Max, Q, QuerySet, When

from .models import Company, Posting, User


def posting_with_applications(
    user: User, queryset: QuerySet | None = None
) -> QuerySet:
    queryset = queryset or Posting.objects.all()
    return queryset.annotate(
        has_application=Max(
            Case(When(application__user=user, then=F("application__pk")))
        )
    )


def posting_queue_set(user: User, ordered: bool = True) -> QuerySet:
    qs = posting_with_applications(
        user=user, queryset=Posting.objects.filter(closed__isnull=True)
    ).filter(Q(has_application__isnull=True))
    if ordered:
        qs = qs.order_by("company__name", "title", "url")
    return qs


def companies_with_postings_count() -> QuerySet:
    return Company.objects.annotate(  # type: ignore
        posting_count=Count("posting")
    )
