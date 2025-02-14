from typing import Any
from collections.abc import Sequence

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, F, Max, Model, QuerySet, When
from django.db.models.functions import Lower
from django.forms import ModelForm, inlineformset_factory
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
from .forms import (
    AddCompanyForm,
    AddPostingForm,
    CompanyChoiceForm,
    URLTextareaForm,
    UserProfileForm,
)
from .models import Application, Company, Posting, User
from .query import (
    companies_with_posting_counts,
    companies_with_wa_counts,
    company_posting_queue_set,
    posting_queue_companies_count,
    posting_queue_set,
    user_application_companies,
    user_companies_leaderboard,
)
from .tables import (
    ApplicationCompanyCountHTMxTable,
    ApplicationHTMxTable,
    CompanyHTMxTable,
    PostingHTMxTable,
    QueueCompanyCountHTMxTable,
    QueueHTMxTable,
)
from .utils import normalize_posting_url


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
        companies = Company.objects.all()
        companies_with_postings = (
            companies_with_posting_counts()
            .filter(open_posting_count__gt=0)
            .order_by("-open_posting_count", Lower("name"))
        )
        your_apps = Application.objects.filter(user=self.request.user)
        your_apps_company_count = user_application_companies(self.request.user)
        posting_queue = posting_queue_set(self.request.user, ordered=False)
        company_posting_queue = company_posting_queue_set(self.request.user)
        posting_queue_companies = posting_queue_companies_count(
            self.request.user
        )
        unreported_apps_count = (
            your_apps.count()
            - your_apps.filter(reported__isnull=False).count()
        )
        return context | {
            "company": companies,
            "companies_with_postings": companies_with_postings,
            "posting": Posting.objects.all(),
            "posting_open": Posting.objects.filter(closed=None),
            "application": Application.objects.all(),
            "your_apps": your_apps,
            "your_apps_company_count": your_apps_company_count,
            "unreported_apps_count": unreported_apps_count,
            "posting_queue": posting_queue,
            "company_posting_queue": company_posting_queue,
            "posting_queue_companies": posting_queue_companies,
            "leaderboard": user_companies_leaderboard(),
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


class AddPostingsView(View):
    form_class_url_textarea = URLTextareaForm
    form_class_add_posting = AddPostingForm
    form_class_select_company = CompanyChoiceForm
    template_name = "main/bulk_add_postings.html"

    def make_formset(self, num: int = 1) -> Any:
        return inlineformset_factory(
            Company,
            Posting,
            form=self.form_class_add_posting,
            min_num=num,
            extra=0,
            can_delete=False,
        )

    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        form = self.form_class_url_textarea()
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
        add_form = AddCompanyForm(request.POST, prefix="add_company")
        company_form = self.form_class_select_company(
            request.POST, prefix="company"
        )
        formset = self.make_formset()(request.POST)
        all_valid = (
            company_form.is_valid()
            and (
                (company := company_form.cleaned_data["company"])
                or add_form.is_valid()
            )
            and formset.is_valid()
        )
        if not all_valid:
            return render(
                request,
                self.template_name,
                self.create_context(
                    form=company_form, add_form=add_form, formset=formset
                ),
            )
        new_saved_postings = []
        posting_matches = []
        if not company:
            company = add_form.save()
        for form in formset:
            if form.cleaned_data["include"] is False:
                continue
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
            ),
        )

    def create_context(self, **context: Any) -> dict[str, Any]:
        if formset := context.get("formset"):
            helper = formset[0].helper
            helper.form_tag = False
            context["helper"] = helper
        context.setdefault("form_title", "Add postings")
        return context

    def process_raw_urls(self, request: HttpRequest) -> HttpResponse:
        form = self.form_class_url_textarea(request.POST)
        if not form.is_valid():
            return render(
                request,
                "main/form.html",
                self.create_context(form=form, submit_text="Process URLs"),
            )
        urls = form.cleaned_data.get("text", "").splitlines()
        urls = [normalize_posting_url(u) for u in urls]
        urls = [u for u in urls if u]
        new_urls, posting_matches = self.check_duplicate_urls(urls)
        if new_urls:
            add_form = AddCompanyForm(prefix="add_company")
            company_form = self.form_class_select_company(prefix="company")
            formset = self.make_formset(num=len(new_urls))(
                initial=[{"url": url} for url in new_urls]
            )
        else:
            add_form = None
            company_form = None
            formset = None
        return render(
            request,
            self.template_name,
            self.create_context(
                posting_matches=posting_matches,
                new_urls=new_urls,
                add_form=add_form,
                form=company_form,
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
    action_links: Sequence[tuple[str, str]] | None = None

    def get_context_data(self, **kwargs: Any) -> Any:
        return super().get_context_data(**kwargs) | {
            "action_links": self.action_links or [],
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
    queryset = companies_with_wa_counts().order_by(Lower("name"))
    export_name = "companies"
    action_links = [("Add company", reverse_lazy("personal:main_company_add"))]


class QueueCompanyCountHTMxTableView(BaseHTMxTableView):
    template_table_title = "Postings queue count by company"
    template_table_htmx_route = "queue_by_company_htmx"
    table_class = QueueCompanyCountHTMxTable
    filterset_class = CompanyFilter
    export_name = "postings_queue_by_company_count"

    def get_queryset(self) -> QuerySet:
        return posting_queue_companies_count(self.request.user)


class ApplicationCompanyCountHTMxTableView(BaseHTMxTableView):
    template_table_title = "Application count by company"
    template_table_htmx_route = "application_by_company_htmx"
    table_class = ApplicationCompanyCountHTMxTable
    filterset_class = CompanyFilter
    export_name = "applications_queue_by_company_count"

    def get_queryset(self) -> QuerySet:
        return user_application_companies(self.request.user)


class FullQueueHTMxTableView(BaseHTMxTableView):
    template_table_title = "Full postings queue"
    template_table_htmx_route = "full_queue_htmx"
    table_class = QueueHTMxTable
    filterset_class = PostingFilter
    export_name = "full_postings_queue"
    action_links = [("Add postings", reverse_lazy("add_postings"))]

    def get_queryset(self) -> QuerySet:
        return posting_queue_set(self.request.user)


class QueueHTMxTableView(FullQueueHTMxTableView):
    template_table_title = "Postings queue"
    template_table_htmx_route = "queue_htmx"
    export_name = "postings_queue"

    def get_queryset(self) -> QuerySet:
        return company_posting_queue_set(self.request.user)


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
        ).order_by(Lower("company__name"), Lower("title"), "url")


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
            Lower("posting__company__name"),
            Lower("posting__title"),
            "posting__url",
        )
