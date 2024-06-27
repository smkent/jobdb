from django_tables2 import Table  # type: ignore

from .models import Company, Posting


class CompanyHTMxTable(Table):
    class Meta:
        model = Company
        template_name = "main/bootstrap_htmx.html"
        sequence = [
            "name",
            "hq",
            "url",
            "careers_url",
            "employees_est",
            "how_found",
            "notes",
        ]
        exclude = [
            "created",
            "careers_urls",
            "id",
            "modified",
            "employees_est_source",
        ]


class QueueHTMxTable(Table):
    class Meta:
        model = Posting
        template_name = "main/bootstrap_htmx.html"
        sequence = [
            "company__name",
            "url",
            "title",
            "notes",
        ]
        fields = [
            "company__name",
            "url",
            "title",
            "notes",
        ]
