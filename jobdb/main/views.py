from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, Count, F, Max, Model, QuerySet, When
from django.forms import ModelForm
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django_filters.views import FilterView  # type: ignore
from django_tables2 import SingleTableMixin  # type: ignore
from django_tables2.export import views as export_views  # type: ignore

from .filters import ApplicationFilter, CompanyFilter, PostingFilter
from .forms import UserProfileForm
from .models import Application, Company, Posting, User
from .query import companies_with_postings_count, posting_queue_set
from .tables import (
    ApplicationHTMxTable,
    CompanyHTMxTable,
    PostingHTMxTable,
    QueueHTMxTable,
)


class ExportMixin(export_views.ExportMixin):
    def get_export_filename(self, export_format: str) -> str:
        if hasattr(self, "get_export_name"):
            export_name = self.get_export_name()
        else:
            export_name = self.export_name
        return f"{export_name}.{export_format}"


class BaseView(LoginRequiredMixin):
    pass


class IndexView(BaseView, TemplateView):
    template_name = "main/index.html"

    def get_context_data(self, **kwargs: Any) -> Any:
        context = super().get_context_data(**kwargs)
        assert isinstance(self.request.user, User)
        your_apps = Application.objects.filter(user=self.request.user)
        your_apps_company_count = (
            your_apps.annotate(company=F("posting__company__name"))
            .values("company")
            .annotate(count=Count("company"))
            .order_by("-count", "company")
        )
        posting_queue = posting_queue_set(self.request.user, ordered=False)
        posting_queue_companies = posting_queue.values(
            "company__name"
        ).annotate(count=Count("pk"))
        unreported_apps_count = (
            your_apps.count()
            - your_apps.filter(reported__isnull=False).count()
        )
        return context | {
            "company": Company.objects.all(),
            "posting": Posting.objects.all(),
            "application": Application.objects.all(),
            "your_apps": your_apps,
            "your_apps_company_count": your_apps_company_count,
            "unreported_apps_count": unreported_apps_count,
            "posting_queue": posting_queue,
            "posting_queue_companies": posting_queue_companies.order_by(
                "-count", "company__name"
            ),
        }


class BaseModelFormView(BaseView, FormView):
    template_name = "main/form.html"

    def form_valid(self, form: ModelForm) -> HttpResponse:
        form.save()
        return super().form_valid(form)

    def get_instance(self) -> Model:
        raise NotImplementedError

    def get_form(self, form_class: type[ModelForm] | None = None) -> ModelForm:
        return (form_class or self.get_form_class())(
            self.request.POST or None, instance=self.get_instance()
        )


class UserProfileFormView(BaseModelFormView):
    template_name = "main/user_profile_form.html"
    form_class = UserProfileForm
    success_url = reverse_lazy("index")

    def get_instance(self) -> Model:
        assert isinstance(self.request.user, User)
        return self.request.user


class BaseHTMxTableView(BaseView, ExportMixin, SingleTableMixin, FilterView):
    template_table_title = "Untitled table"
    template_table_htmx_route = ""
    paginate_by = 15

    def get_context_data(self, **kwargs: Any) -> Any:
        return super().get_context_data(**kwargs) | {
            "table_title": self.template_table_title,
            "table_htmx_route": reverse(self.template_table_htmx_route),
        }

    def get_template_names(self) -> str:
        if self.request.htmx:
            return "main/table_partial.html"
        return "main/table_htmx.html"


class CompanyHTMxTableView(BaseHTMxTableView):
    template_table_title = "All companies"
    template_table_htmx_route = "company_htmx"
    table_class = CompanyHTMxTable
    filterset_class = CompanyFilter
    queryset = companies_with_postings_count()
    export_name = "companies"


class QueueHTMxTableView(BaseHTMxTableView):
    template_table_title = "Postings queue"
    template_table_htmx_route = "queue_htmx"
    table_class = QueueHTMxTable
    filterset_class = PostingFilter
    export_name = "postings_queue"

    def get_queryset(self) -> QuerySet:
        return posting_queue_set(self.request.user)


class PostingHTMxTableView(QueueHTMxTableView):
    template_table_title = "All postings"
    template_table_htmx_route = "posting_htmx"
    table_class = PostingHTMxTable
    filterset_class = PostingFilter
    export_name = "postings"

    def get_queryset(self) -> QuerySet:
        return Posting.objects.annotate(
            applied=Max(
                Case(
                    When(
                        application__user=self.request.user,
                        then=F("application__applied"),
                    )
                )
            ),
            reported=Max(
                Case(
                    When(
                        application__user=self.request.user,
                        then=F("application__reported"),
                    )
                )
            ),
        ).order_by("company__name", "title", "url")


class ApplicationHTMxTableView(BaseHTMxTableView):
    template_table_title = "Your applications"
    template_table_htmx_route = "application_htmx"
    table_class = ApplicationHTMxTable
    filterset_class = ApplicationFilter

    def get_export_name(self) -> str:
        base_name = "applications"
        if (
            reported := self.filterset.form.cleaned_data.get("reported")
        ) is not None:
            return base_name + "-" + ("reported" if reported else "unreported")
        return base_name

    def get_queryset(self) -> QuerySet:
        return Application.objects.filter(user=self.request.user).order_by(
            "-applied",
            "posting__company__name",
            "posting__title",
            "posting__url",
        )
