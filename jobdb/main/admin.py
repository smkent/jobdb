from functools import partial
from typing import Any

from django.contrib.admin import ModelAdmin, display, register
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import QuerySet
from django.forms import ModelForm
from django.http import HttpRequest
from django.utils.html import format_html

from ..admin import personal_admin_site
from .models import APIKey, Application, Company, Posting, User

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


class APIKeyAdminForm(ModelForm):
    class Meta:
        model = APIKey
        exclude = ["key"]


@register(APIKey)
class APIKeyAdmin(ModelAdmin):
    ordering = ["user__username", "key", "-created"]
    list_display = ["user", "key", "created"]
    list_display_links = ["key"]
    form = APIKeyAdminForm


class APIKeyPortalAdminForm(APIKeyAdminForm):
    current_user: User

    class Meta(APIKeyAdminForm.Meta):
        exclude = APIKeyAdminForm.Meta.exclude + ["user"]


@register_portal(APIKey)
class APIKeyPortalAdmin(ModelAdmin):
    list_display = ["key", "created"]
    form = APIKeyPortalAdminForm

    def save_model(
        self, request: HttpRequest, obj: APIKey, *args: Any, **kwargs: Any
    ) -> None:
        obj.user = request.user
        super().save_model(request, obj, *args, **kwargs)


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


class ApplicationAdminBase(ModelAdmin):
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


class ApplicationPortalAdminForm(ModelForm):
    current_user: User

    class Meta:
        model = Application
        exclude = ["user"]


@register_portal(Application)
class ApplicationPortalAdmin(ApplicationAdminBase):
    form = ApplicationPortalAdminForm

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).filter(user=request.user)

    def save_model(
        self, request: HttpRequest, obj: Application, *args: Any, **kwargs: Any
    ) -> None:
        obj.user = request.user
        super().save_model(request, obj, *args, **kwargs)


@register(Application)
class ApplicationAdmin(ApplicationAdminBase):
    list_display = ["user"] + ApplicationAdminBase.list_display  # type: ignore
