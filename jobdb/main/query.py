from django.db.models import Q, QuerySet

from .models import Posting, User


def posting_queue_set(user: User, ordered: bool = True) -> QuerySet:
    qs = (
        Posting.objects.filter(closed__isnull=True)
        .annotate(has_application=Q(application__user=user))
        .filter(has_application__isnull=True)
    )
    if ordered:
        qs = qs.order_by("company__name", "title", "url")
    return qs
