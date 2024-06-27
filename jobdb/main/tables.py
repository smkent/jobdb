from typing import Any

from django.urls import reverse
from django.utils.html import format_html
from django_tables2 import Column  # type: ignore
from django_tables2 import Table

from .models import Posting


class QueueHTMxTable(Table):
    company__name = Column(attrs={"th": {"style": "width: 200px;"}})
    url = Column(attrs={"th": {"style": "width: 500px;"}})
    title = Column(attrs={"th": {"style": "width: 400px;"}})

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

    def render_url(self, value: str, record: Any) -> str:
        return format_html(f'<a href="{value}">{record.url_text}</a>')

    def render_title(self, value: str, record: Any) -> str:
        portal_url = reverse("personal:main_posting_change", args=(record.pk,))
        return format_html(f'<a href="{portal_url}">{value}</a>')

    def render_company__name(self, value: str, record: Any) -> str:
        portal_url = reverse(
            "personal:main_company_change", args=(record.company.pk,)
        )
        return format_html(f'<a href="{portal_url}">{value}</a>')
