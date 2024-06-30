import os
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
    posting_count = Column(
        verbose_name="Postings", attrs={"th": {"style": "width: 120px;"}}
    )
    url = Column(attrs={"th": {"style": "width: 200px;"}})
    careers_urls = Column(
        verbose_name="Careers URLs",
        empty_values=(),
        attrs={"th": {"style": "width: 200px;"}},
    )
    employees_est = Column(
        verbose_name="# employees",
        attrs={"th": {"style": "width: 200px;"}},
    )
    employees_est_source = Column(visible=False)
    how_found = Column(visible=False)
    created = Column(
        verbose_name="Added", attrs={"th": {"style": "width: 200px;"}}
    )

    class Meta:
        model = Company
        template_name = "main/bootstrap_htmx.html"
        sequence = [
            "name",
            "url",
            "careers_urls",
            "hq",
            "posting_count",
            "employees_est",
            "employees_est_source",
            "how_found",
            "created",
            "notes",
        ]
        fields = [
            "name",
            "url",
            "careers_urls",
            "hq",
            "posting_count",
            "employees_est",
            "employees_est_source",
            "how_found",
            "created",
            "notes",
        ]

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

    def value_careers_urls(self, record: Any) -> str:
        urls = []
        urls.append(record.careers_url)
        urls += record.careers_urls or []
        return os.linesep.join(urls)

    def render_careers_urls(self, record: Any) -> str:
        value = self.value_careers_urls(record)
        if not value:
            return str(self.default)
        rendered_urls = []
        for url in value.strip().split(os.linesep):
            rendered_urls.append(format_html(f'<a href="{url}">{url}</a>'))
        return format_html("<br />".join(rendered_urls))

    def render_created(self, value: datetime, record: Any) -> str:
        return localize(value.date())

    def render_posting_count(self, value: Any, record: Any) -> str:
        url = reverse("posting_htmx") + f"?company={record.name}"
        return format_html(f'<a href="{url}">{value}</a>')

    def value_posting_count(self, value: Any) -> Any:
        return value


class QueueHTMxTable(Table):
    company__name = Column(attrs={"th": {"style": "width: 200px;"}})
    job_board_urls = Column(visible=False)
    url = Column(attrs={"th": {"style": "width: 500px;"}})
    title = Column(attrs={"th": {"style": "width: 400px;"}})
    created = Column(
        verbose_name="Added", attrs={"th": {"style": "width: 200px;"}}
    )

    class Meta:
        model = Posting
        template_name = "main/bootstrap_htmx.html"
        sequence = [
            "company__name",
            "job_board_urls",
            "url",
            "title",
            "created",
            "notes",
        ]
        fields = [
            "company__name",
            "job_board_urls",
            "url",
            "title",
            "created",
            "notes",
        ]

    def render_url(self, value: str, record: Any) -> str:
        return format_html(
            f'<a href="{value}" target="_blank" rel="noopener noreferrer">'
            f"{record.url_text}</a>"
        )

    def value_url(self, value: str) -> str:
        return value

    def value_job_board_urls(self, record: Any) -> str:
        return os.linesep.join(record.job_board_urls or [])

    def render_job_board_urls(self, record: Any) -> str:
        value = self.value_job_board_urls(record)
        if not value:
            return str(self.default)
        rendered_urls = []
        for url in value.strip().split(os.linesep):
            rendered_urls.append(format_html(f'<a href="{url}">{url}</a>'))
        return format_html("<br />".join(rendered_urls))

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

    def render_created(self, value: datetime, record: Any) -> str:
        return localize(value.date())


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
            "job_board_urls",
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
            "job_board_urls",
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
