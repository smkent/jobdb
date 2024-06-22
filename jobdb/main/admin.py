from functools import partial

from django.contrib.admin import ModelAdmin, display, register
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from ..admin import personal_admin_site
from .models import Application, Company, Posting, User

register_portal = partial(register, site=personal_admin_site)


def clickable_url_html(
    url: str, display: str = "", target: str = "_blank"
) -> str:
    return format_html(
        '<a href="{0}" target="{2}">{1}</a>', url, display or url, target
    )


@register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["username"]


@register(Company)
@register_portal(Company)
class CompanyAdmin(ModelAdmin):
    list_display = ["name", "url_clickable", "careers_url_clickable", "hq"]
    ordering = ["name"]

    @display(description=Company._meta.get_field("url").verbose_name)
    def url_clickable(self, obj: Company) -> str:
        return clickable_url_html(obj.url)

    @display(description=Company._meta.get_field("careers_url").verbose_name)
    def careers_url_clickable(self, obj: Company) -> str:
        return clickable_url_html(obj.careers_url)


@register(Posting)
@register_portal(Posting)
class PostingAdmin(ModelAdmin):
    list_display = [
        "company_name",
        "title",
        "url_clickable",
        "is_closed",
        "location",
    ]
    list_display_links = ["title"]
    list_filter = ["company__name"]
    ordering = ["company__name", "title", "url"]

    @display(description=Company._meta.get_field("name").verbose_name)
    def company_name(self, obj: Company) -> str:
        assert isinstance(obj.company.name, str)
        return clickable_url_html(
            f"../company/{obj.company.pk}/change/",
            obj.company.name,
            target="_self",
        )

    @display(description=Posting._meta.get_field("url").verbose_name)
    def url_clickable(self, obj: Posting) -> str:
        return clickable_url_html(obj.url)

    @display(description="Closed")
    def is_closed(self, obj: Posting) -> str:
        return "Yes" if bool(obj.closed) else "No"


@register_portal(Application)
class ApplicationPortalAdmin(ModelAdmin):
    list_display = ["summary", "applied", "reported", "bona_fide"]
    list_display_links = ["summary"]
    list_filter = ["bona_fide", "posting__company__name"]
    ordering = [
        "-applied",
        "user",
        "posting__company__name",
        "posting__title",
        "posting__url",
    ]

    @display(description="Application")
    def summary(self, obj: Application) -> str:
        return f"{obj.posting.company.name} • {obj.posting.title}"


@register(Application)
class ApplicationAdmin(ApplicationPortalAdmin):
    list_display = [
        "user"
    ] + ApplicationPortalAdmin.list_display  # type: ignore
