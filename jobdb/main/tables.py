from typing import Any

from django.urls import reverse
from django.utils.html import format_html
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

    def render_title(self, value: str, record: Any) -> str:
        portal_url = reverse("personal:main_posting_change", args=(record.pk,))
        return format_html(f'<a href="{portal_url}">{value}</a>')
