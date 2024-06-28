from functools import partial, wraps
from typing import Any, Callable

from django.conf import settings
from django.contrib.admin import (
    ModelAdmin,
    SimpleListFilter,
    action,
    display,
    register,
    site,
)
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet
from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.html import format_html

from ..admin import personal_admin_site
from .models import APIKey, Application, Company, Posting, User

register_portal = partial(register, site=personal_admin_site)


site.login = staff_member_required(  # type: ignore
    site.login, login_url=settings.LOGIN_URL
)
personal_admin_site.login = login_required(  # type: ignore
    personal_admin_site.login
)


MAFunc = Callable[[ModelAdmin, HttpRequest, QuerySet], Any]


def require_confirmation(
    func: Any = None,
    queryset_filter: Callable[[QuerySet], QuerySet] | None = None,
) -> Any:
    def _decorator(func: MAFunc) -> MAFunc:
        @wraps(func)
        def _wrapper(
            ma: ModelAdmin, request: HttpRequest, queryset: QuerySet
        ) -> Any:
            if queryset_filter:
                queryset = queryset_filter(queryset)
            if not queryset:
                return None
            if request.POST.get("confirmation") is None:
                request.current_app = ma.admin_site.name
                context = {
                    "action": request.POST["action"],
                    "queryset": queryset,
                    "opts": ma.model._meta,
                    "description": (
                        getattr(ma, request.POST["action"]).short_description
                    ),
                    "view_name": (
                        f"{ma.admin_site.name}"
                        ":"
                        f"{ma.model._meta.app_label}"
                        f"_{ma.model._meta.model_name}_change"
                    ),
                }
                return TemplateResponse(
                    request, "admin/my_action_confirmation.html", context
                )

            return func(ma, request, queryset)

        return _wrapper

    if func:
        return _decorator(func)
    return _decorator


def clickable_url_html(
    url: str, display: str = "", target: str = "_blank"
) -> str:
    return format_html(
        '<a href="{0}" target="{2}">{1}</a>', url, display or url, target
    )


@register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["username"]


@register(APIKey)
class APIKeyAdmin(ModelAdmin):
    ordering = ["user__username", "created", "key"]
    list_display = ["user", "key", "comment", "created"]
    list_display_links = ["key"]
    exclude = ["key"]

    def get_readonly_fields(
        self, request: HttpRequest, obj: APIKey | None = None
    ) -> list[str]:
        return ["comment", "user"] if obj else []


@register_portal(APIKey)
class APIKeyPortalAdmin(ModelAdmin):
    ordering = ["user__username", "created", "key"]
    list_display = ["key", "comment", "created"]
    exclude = ["user", "key"]

    def save_model(
        self, request: HttpRequest, obj: APIKey, *args: Any, **kwargs: Any
    ) -> None:
        obj.user = request.user
        super().save_model(request, obj, *args, **kwargs)

    def get_readonly_fields(
        self, request: HttpRequest, obj: APIKey | None = None
    ) -> list[str]:
        return ["comment"] if obj else []


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


class PostingClosedFilter(SimpleListFilter):
    title = "Closed"
    parameter_name = "closed"

    def lookups(
        self, request: HttpRequest, model_admin: ModelAdmin
    ) -> list[tuple[str, str]]:
        return [("open", "Open"), ("closed", "Closed")]

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if self.value() == "open":
            return queryset.filter(closed=None)
        elif self.value() == "closed":
            return queryset.filter(closed__isnull=False)
        return queryset


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
    list_filter = [PostingClosedFilter]
    ordering = ["company__name", "title", "url"]
    actions = ["mark_closed"]

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

    @action(description="Mark selected postings as closed")
    @require_confirmation(queryset_filter=lambda qs: qs.filter(closed=None))
    def mark_closed(self, request: HttpRequest, queryset: QuerySet) -> Any:
        queryset.update(closed=timezone.now())


class ApplicationAdminBase(ModelAdmin):
    list_display = ["summary", "applied", "reported", "bona_fide"]
    list_display_links = ["summary"]
    list_filter = ["reported", "bona_fide"]
    ordering = [
        "-applied",
        "user",
        "posting__company__name",
        "posting__title",
        "posting__url",
    ]
    actions = ["mark_reported"]

    @display(description="Application")
    def summary(self, obj: Application) -> str:
        return f"{obj.posting.company.name} • {obj.posting.title}"

    @action(description="Mark selected applications as reported")
    @require_confirmation(queryset_filter=lambda qs: qs.filter(reported=None))
    def mark_reported(self, request: HttpRequest, queryset: QuerySet) -> Any:
        queryset.update(reported=timezone.now())


@register_portal(Application)
class ApplicationPortalAdmin(ApplicationAdminBase):
    exclude = ["user"]

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
