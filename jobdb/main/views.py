from typing import Any

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django_filters.views import FilterView  # type: ignore
from django_tables2 import SingleTableMixin  # type: ignore

from .filters import QueueFilter
from .models import Application, Company, Posting, User
from .query import posting_queue_set
from .tables import QueueHTMxTable


@login_required
def index(request: HttpRequest) -> HttpResponse:
    your_apps = Application.objects.filter(user=request.user)
    assert isinstance(request.user, User)
    posting_queue = posting_queue_set(request.user, ordered=False)
    posting_queue_company_count = (
        posting_queue.values("company__name")
        .annotate(count=Count("pk"))
        .count()
    )
    return render(
        request,
        "main/index.html",
        {
            "company": Company.objects.all(),
            "posting": Posting.objects.all(),
            "application": Application.objects.all(),
            "your_apps": your_apps,
            "reported_apps": your_apps.filter(reported__isnull=False),
            "posting_queue": posting_queue,
            "posting_queue_company_count": posting_queue_company_count,
        },
    )


class BaseHTMxTableView(LoginRequiredMixin, SingleTableMixin, FilterView):
    template_table_title = "Untitled table"
    template_table_htmx_route = ""
    paginate_by = 15

    def get_context_data(self, **kwargs: Any) -> Any:
        return super().get_context_data(**kwargs) | {
            "table_title": self.template_table_title,
            "table_htmx_route": reverse(self.template_table_htmx_route),
        }

    def get_template_names(self) -> str:
        if self.request.htmx:
            return "main/table_partial.html"
        return "main/table_htmx.html"


class QueueHTMxTableView(BaseHTMxTableView):
    template_table_title = "Postings queue"
    template_table_htmx_route = "queue_htmx"
    table_class = QueueHTMxTable
    filterset_class = QueueFilter

    def get_queryset(self) -> QuerySet:
        return posting_queue_set(self.request.user)
