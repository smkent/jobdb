from typing import Any

from django.contrib.auth.decorators import login_required
from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django_filters.views import FilterView  # type: ignore
from django_tables2 import SingleTableMixin  # type: ignore

from .filters import CompanyFilter, QueueFilter
from .models import Application, Company, Posting
from .tables import CompanyHTMxTable, QueueHTMxTable


@login_required
def index(request: HttpRequest) -> HttpResponse:
    your_apps = Application.objects.filter(user=request.user)
    return render(
        request,
        "main/index.html",
        {
            "company": Company.objects.all(),
            "posting": Posting.objects.all(),
            "application": Application.objects.all(),
            "your_apps": your_apps,
        },
    )


class BaseHTMxTableView(SingleTableMixin, FilterView):
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


class CompanyHTMxTableView(BaseHTMxTableView):
    template_table_title = "Companies"
    template_table_htmx_route = "company_htmx"
    table_class = CompanyHTMxTable
    queryset = Company.objects.all()
    filterset_class = CompanyFilter


class QueueHTMxTableView(BaseHTMxTableView):
    template_table_title = "Postings queue"
    template_table_htmx_route = "queue_htmx"
    table_class = QueueHTMxTable
    filterset_class = QueueFilter

    def get_queryset(self) -> QuerySet:
        return (
            Posting.objects.filter(closed__isnull=True)
            .annotate(has_application=Q(application__user=self.request.user))
            .filter(has_application__isnull=True)
            .order_by("company__name", "title", "url")
        )
