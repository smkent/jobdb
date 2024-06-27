from django_tables2 import Table  # type: ignore

from .models import Posting


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
