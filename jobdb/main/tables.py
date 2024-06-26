from django_tables2 import Table  # type: ignore

from .models import Company


class CompanyHTMxTable(Table):
    class Meta:
        model = Company
        template_name = "main/bootstrap_htmx.html"
