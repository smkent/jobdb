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
from import_export.admin import (  # type: ignore
    ExportActionMixin,
    ImportExportMixin,
)

from ..admin import personal_admin_site
from ..main.query import posting_with_applications
from .models import APIKey, Application, Company, Posting, Priority, User
from .resources import (
    ApplicationResource,
    CompanyResource,
    PostingResource,
    UserApplicationResource,
    UserResource,
)

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
class UserAdmin(ImportExportMixin, ExportActionMixin, BaseUserAdmin):
    ordering = ["username"]
    resource_classes = [UserResource]

    def get_data_for_export(
        self, request: HttpRequest, queryset: QuerySet, **kwargs: Any
    ) -> Any:
        queryset = queryset.exclude(username="admin")
        return super().get_data_for_export(request, queryset, **kwargs)


@register(APIKey)
class APIKeyAdmin(ImportExportMixin, ExportActionMixin, ModelAdmin):
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

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).filter(user=request.user)


@register(Company)
@register_portal(Company)
class CompanyAdmin(ImportExportMixin, ExportActionMixin, ModelAdmin):
    list_display = [
        "name",
        "url_clickable",
        "careers_url_clickable",
        "priority",
        "filed",
    ]
    list_filter = ["priority", "filed"]
    ordering = ["name"]
    actions = [
        "mark_priority_high",
        "mark_priority_normal",
        "mark_priority_low",
    ]
    search_fields = ["name", "url"]
    resource_classes = [CompanyResource]

    @display(description=Company._meta.get_field("url").verbose_name)
    def url_clickable(self, obj: Company) -> str:
        return clickable_url_html(obj.url, display=obj.url_text)

    @display(description=Company._meta.get_field("careers_url").verbose_name)
    def careers_url_clickable(self, obj: Company) -> str:
        return clickable_url_html(
            obj.careers_url, display=obj.careers_url_text
        )

    @action(description="Mark selected companies as high priority")
    @require_confirmation
    def mark_priority_high(
        self, request: HttpRequest, queryset: QuerySet
    ) -> Any:
        queryset.update(priority=Priority.HIGH)

    @action(description="Mark selected companies as normal priority")
    @require_confirmation
    def mark_priority_normal(
        self, request: HttpRequest, queryset: QuerySet
    ) -> Any:
        queryset.update(priority=Priority.NORMAL)

    @action(description="Mark selected companies as low priority")
    @require_confirmation
    def mark_priority_low(
        self, request: HttpRequest, queryset: QuerySet
    ) -> Any:
        queryset.update(priority=Priority.LOW)


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
class PostingAdmin(ImportExportMixin, ExportActionMixin, ModelAdmin):
    list_display = [
        "company_name",
        "title",
        "url_clickable",
        "in_wa",
        "closed",
        "created",
    ]
    list_display_links = ["title"]
    list_filter = [PostingClosedFilter, "in_wa"]
    ordering = ["company__name", "title", "url"]
    actions = ["mark_applied", "mark_closed"]
    search_fields = ["company__name", "title", "url"]
    resource_classes = [PostingResource]

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
        return clickable_url_html(obj.url, display=obj.url_text)

    @action(description="Mark selected postings as closed")
    @require_confirmation(queryset_filter=lambda qs: qs.filter(closed=None))
    def mark_closed(self, request: HttpRequest, queryset: QuerySet) -> Any:
        queryset.update(closed=timezone.now())

    @action(description="Create application entries for selected postings")
    @require_confirmation
    def mark_applied(self, request: HttpRequest, queryset: QuerySet) -> Any:
        assert isinstance(request.user, User)
        for posting in posting_with_applications(
            user=request.user, queryset=queryset
        ).filter(has_application=False):
            application = Application(posting=posting, user=request.user)
            application.save()


class ApplicationAdminBase(ImportExportMixin, ExportActionMixin, ModelAdmin):
    list_display = [
        "company_name",
        "role_title",
        "url_clickable",
        "in_wa",
        "applied",
        "reported",
        "bona_fide",
    ]
    list_display_links = ["role_title"]
    list_filter = ["reported", "bona_fide", "posting__in_wa"]
    ordering = [
        "-applied",
        "user",
        "posting__company__name",
        "posting__title",
        "posting__url",
    ]
    search_fields = [
        "posting__company__name",
        "posting__title",
        "posting__url",
    ]
    actions = ["mark_reported"]

    @display(description=Company._meta.get_field("name").verbose_name)
    def company_name(self, obj: Company) -> str:
        assert isinstance(obj.posting.company.name, str)
        return clickable_url_html(
            f"../company/{obj.posting.company.pk}/change/",
            obj.posting.company.name,
            target="_self",
        )

    @display(description="Title")
    def role_title(self, obj: Application) -> Any:
        return obj.posting.title

    @display(description=Posting._meta.get_field("url").verbose_name)
    def url_clickable(self, obj: Application) -> str:
        return clickable_url_html(
            obj.posting.url, display=obj.posting.url_text
        )

    @display(description="In WA", boolean=True)
    def in_wa(self, obj: Application) -> Any:
        return obj.posting.in_wa

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
    resource_classes = [UserApplicationResource]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).filter(user=request.user)

    def save_model(
        self, request: HttpRequest, obj: Application, *args: Any, **kwargs: Any
    ) -> None:
        obj.user = request.user
        super().save_model(request, obj, *args, **kwargs)

    def get_data_for_export(
        self, request: HttpRequest, queryset: QuerySet, **kwargs: Any
    ) -> Any:
        queryset = queryset.filter(user=request.user)
        return super().get_data_for_export(request, queryset, **kwargs)

    def get_import_resource_kwargs(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> dict[str, Any]:
        kwargs = super().get_resource_kwargs(request, *args, **kwargs)
        return kwargs | {"user": request.user}

    def get_export_filename(self, *args: Any, **kwargs: Any) -> str:
        default_file_name = super().get_export_filename(*args, **kwargs)
        return f"Personal-{default_file_name}"


@register(Application)
class ApplicationAdmin(ApplicationAdminBase):
    list_display = ["user"] + ApplicationAdminBase.list_display  # type: ignore
    resource_classes = [ApplicationResource]
