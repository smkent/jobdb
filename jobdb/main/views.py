from typing import Any, Sequence

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, Count, F, Max, Model, QuerySet, When
from django.forms import ModelForm, formset_factory
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django_filters.views import FilterView  # type: ignore
from django_tables2 import SingleTableMixin  # type: ignore
from django_tables2.export import views as export_views  # type: ignore

from .filters import (
    AllPostingFilter,
    ApplicationFilter,
    CompanyFilter,
    PostingFilter,
)
from .forms import AddPostingForm, URLTextareaForm, UserProfileForm
from .models import Application, Company, Posting, User
from .query import (
    companies_with_postings_count,
    leaderboard_application_companies,
    posting_queue_set,
)
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
        leaderboard = (
            Application.objects.values("user__username", "user__first_name")
            .annotate(count=Count("user"))
            .order_by("-count", "user__username")
        )
        leaderboard_companies = leaderboard_application_companies()
        return context | {
            "company": Company.objects.all(),
            "posting": Posting.objects.all(),
            "posting_open": Posting.objects.filter(closed=None),
            "application": Application.objects.all(),
            "your_apps": your_apps,
            "your_apps_company_count": your_apps_company_count,
            "unreported_apps_count": unreported_apps_count,
            "posting_queue": posting_queue,
            "posting_queue_companies": posting_queue_companies.order_by(
                "-count", "company__name"
            ),
            "leaderboard": leaderboard,
            "leaderboard_companies": leaderboard_companies,
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


class AddPostingsBulkTool(View):
    form_class_1 = URLTextareaForm
    form_class_2 = AddPostingForm
    template_name = "main/bulk_add_postings.html"

    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        form = self.form_class_1()
        return render(
            request,
            "main/form.html",
            self.create_context(form=form, submit_text="Process URLs"),
        )

    def post(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        if request.POST.get("tool") == "urls_submitted":
            return self.process_raw_urls(request)
        formset = formset_factory(self.form_class_2)(request.POST)
        company = Company.objects.get(pk=request.POST["company"])
        if not formset.is_valid():
            return render(
                request,
                self.template_name,
                self.create_context(formset=formset, company=company.pk),
            )
        new_saved_postings = []
        posting_matches = []
        for form in formset:
            if posting := Posting.objects.by_url(  # type: ignore
                form.cleaned_data["url"]
            ).first():
                posting_matches.append(posting)
                continue
            form.instance.company = company
            obj = form.save()
            new_saved_postings.append(obj)
        return render(
            request,
            self.template_name,
            self.create_context(
                posting_matches=posting_matches,
                new_saved_postings=new_saved_postings,
                company=company.pk,
            ),
        )

    def create_context(self, **context: Any) -> dict[str, Any]:
        context.setdefault("form_title", "Bulk add postings")
        if formset := context.get("formset"):
            helper = formset[0].helper
            helper.form_tag = False
            context["helper"] = helper
            context.setdefault(
                "companies",
                Company.objects.order_by("name"),
            )
        return context

    def process_raw_urls(self, request: HttpRequest) -> HttpResponse:
        form = self.form_class_1(request.POST)
        if not form.is_valid():
            return render(
                request,
                "main/form.html",
                self.create_context(form=form, submit_text="Process URLs"),
            )
        urls = form.cleaned_data.get("text", "").splitlines()
        new_urls, posting_matches = self.check_duplicate_urls(urls)
        if new_urls:
            formset = formset_factory(self.form_class_2, extra=0)(
                initial=[{"url": url} for url in new_urls]
            )
        else:
            formset = None
        return render(
            request,
            self.template_name,
            self.create_context(
                posting_matches=posting_matches,
                new_urls=new_urls,
                formset=formset,
            ),
        )

    def check_duplicate_urls(
        self, urls: Sequence[str]
    ) -> tuple[set[str], dict[str, Posting]]:
        new_urls = set()
        posting_matches = {}
        for url in urls:
            if postings := Posting.objects.by_url(url):  # type: ignore
                posting_matches[url] = postings.first()
            else:
                new_urls.add(url)
        return new_urls, posting_matches


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
    filterset_class = AllPostingFilter
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
