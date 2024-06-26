from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django_filters.views import FilterView  # type: ignore
from django_tables2 import SingleTableMixin  # type: ignore

from .filters import CompanyFilter
from .models import Application, Company, Posting
from .tables import CompanyHTMxTable


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


class CompanyHTMxTableView(SingleTableMixin, FilterView):
    table_class = CompanyHTMxTable
    queryset = Company.objects.all()
    filterset_class = CompanyFilter
    paginate_by = 15

    def get_template_names(self) -> str:
        if self.request.htmx:
            return "main/company_table_partial.html"
        return "main/company_table_htmx.html"
