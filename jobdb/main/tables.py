from datetime import datetime, timezone
from typing import Any

from django.urls import reverse
from django.utils.formats import localize
from django.utils.html import format_html
from django_tables2 import Column  # type: ignore
from django_tables2 import DateTimeColumn as BaseDateTimeColumn
from django_tables2 import Table

from .models import Application, Company, Posting


class DateTimeColumn(BaseDateTimeColumn):
    def render(self, value: datetime | None, *args: Any, **kwargs: Any) -> Any:
        if not value:
            return super().render(*args, value=value, **kwargs)
        return value.astimezone(timezone.utc).replace(tzinfo=None).date()


class CompanyHTMxTable(Table):
    name = Column(attrs={"th": {"style": "width: 200px;"}})
    hq = Column(attrs={"th": {"style": "width: 200px;"}})
    url = Column(attrs={"th": {"style": "width: 200px;"}})
    careers_url = Column(visible=False)
    employees_est = Column(
        verbose_name="Est. # employees",
        attrs={"th": {"style": "width: 200px;"}},
    )
    employees_est_source = Column(visible=False)
    how_found = Column(visible=False)

    class Meta:
        model = Company
        template_name = "main/bootstrap_htmx.html"
        sequence = [
            "name",
            "url",
            "careers_url",
            "hq",
            "employees_est",
            "employees_est_source",
            "how_found",
            "notes",
        ]
        fields = ["name", "url", "careers_url", "hq", "employees_est", "notes"]

    def render_url(self, value: str, record: Any) -> str:
        return format_html(
            f'<a href="{value}" target="_blank" rel="noopener noreferrer">'
            f"{record.url_text}</a>"
        )

    def value_url(self, value: str) -> str:
        return value

    def render_name(self, value: str, record: Any) -> str:
        portal_url = reverse("personal:main_company_change", args=(record.pk,))
        return format_html(f'<a href="{portal_url}">{value}</a>')

    def value_name(self, value: str) -> str:
        return value


class QueueHTMxTable(Table):
    company__name = Column(attrs={"th": {"style": "width: 200px;"}})
    url = Column(attrs={"th": {"style": "width: 500px;"}})
    title = Column(attrs={"th": {"style": "width: 400px;"}})

    class Meta:
        model = Posting
        template_name = "main/bootstrap_htmx.html"
        sequence = ["company__name", "url", "title", "notes"]
        fields = ["company__name", "url", "title", "notes"]

    def render_url(self, value: str, record: Any) -> str:
        return format_html(
            f'<a href="{value}" target="_blank" rel="noopener noreferrer">'
            f"{record.url_text}</a>"
        )

    def value_url(self, value: str) -> str:
        return value

    def render_title(self, value: str, record: Any) -> str:
        portal_url = reverse("personal:main_posting_change", args=(record.pk,))
        return format_html(f'<a href="{portal_url}">{value}</a>')

    def value_title(self, value: str) -> str:
        return value

    def render_company__name(self, value: str, record: Any) -> str:
        portal_url = reverse(
            "personal:main_company_change", args=(record.company.pk,)
        )
        return format_html(f'<a href="{portal_url}">{value}</a>')

    def value_company__name(self, value: str) -> str:
        return value


class PostingHTMxTable(QueueHTMxTable):
    closed = Column(
        verbose_name="Closed",
        attrs={"th": {"style": "width: 100px;"}},
    )
    applied = DateTimeColumn(
        attrs={"th": {"style": "width: 150px;"}},
    )
    reported = DateTimeColumn(attrs={"th": {"style": "width: 150px;"}})
    location = Column(visible=False)
    wa_jurisdiction = Column(visible=False)

    class Meta:
        model = Posting
        template_name = "main/bootstrap_htmx.html"
        sequence = [
            "company__name",
            "url",
            "title",
            "closed",
            "location",
            "wa_jurisdiction",
            "applied",
            "reported",
            "notes",
        ]
        fields = [
            "company__name",
            "url",
            "title",
            "closed",
            "location",
            "wa_jurisdiction",
            "applied",
            "reported",
            "notes",
        ]
        row_attrs = {
            "class": lambda record: ("posting-closed" if record.closed else "")
        }

    def render_closed(self, value: Any) -> Any:
        return "Yes" if value else ()


class ApplicationHTMxTable(Table):
    posting__company__name = Column(attrs={"th": {"style": "width: 200px;"}})
    posting__url = Column(attrs={"th": {"style": "width: 500px;"}})
    posting__title = Column(attrs={"th": {"style": "width: 400px;"}})
    applied = DateTimeColumn(
        attrs={"th": {"style": "width: 150px;"}},
    )
    reported = DateTimeColumn(attrs={"th": {"style": "width: 150px;"}})

    class Meta:
        model = Application
        template_name = "main/bootstrap_htmx.html"
        sequence = [
            "posting__company__name",
            "posting__url",
            "posting__title",
            "applied",
            "reported",
            "bona_fide",
            "notes",
        ]
        fields = [
            "posting__company__name",
            "posting__url",
            "posting__title",
            "applied",
            "reported",
            "bona_fide",
            "notes",
        ]

    def render_posting__url(self, value: str, record: Any) -> str:
        return format_html(f'<a href="{value}">{record.posting.url_text}</a>')

    def value_posting__url(self, value: str) -> str:
        return value

    def render_posting__title(self, value: str, record: Any) -> str:
        portal_url = reverse(
            "personal:main_posting_change", args=(record.posting.pk,)
        )
        return format_html(f'<a href="{portal_url}">{value}</a>')

    def value_posting__title(self, value: str) -> str:
        return value

    def render_posting__company__name(self, value: str, record: Any) -> str:
        portal_url = reverse(
            "personal:main_company_change", args=(record.posting.company.pk,)
        )
        return format_html(f'<a href="{portal_url}">{value}</a>')

    def value_posting__company__name(self, value: str) -> str:
        return value

    def render_applied(self, value: datetime, record: Any) -> str:
        portal_url = reverse(
            "personal:main_application_change", args=(record.pk,)
        )
        value_str = localize(value.date())
        return format_html(f'<a href="{portal_url}">{value_str}</a>')

    def value_applied(self, value: Any) -> Any:
        if not value:
            return value
        return value.astimezone(timezone.utc).replace(tzinfo=None).date()
