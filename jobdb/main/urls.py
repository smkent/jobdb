from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path(
        "profile",
        views.UserProfileFormView.as_view(),
        name="user_profile_edit",
    ),
    path(
        "companies", views.CompanyHTMxTableView.as_view(), name="company_htmx"
    ),
    path(
        "companies/completion_stats",
        views.CompanyCompletionStatsHTMxTableView.as_view(),
        name="company_completion_stats_htmx",
    ),
    path(
        "postings", views.PostingHTMxTableView.as_view(), name="posting_htmx"
    ),
    path(
        "applications",
        views.ApplicationHTMxTableView.as_view(),
        name="application_htmx",
    ),
    path(
        "applications/by_company",
        views.ApplicationCompanyCountHTMxTableView.as_view(),
        name="application_by_company_htmx",
    ),
    path("queue", views.QueueHTMxTableView.as_view(), name="queue_htmx"),
    path(
        "queue/by_company",
        views.QueueCompanyCountHTMxTableView.as_view(),
        name="queue_by_company_htmx",
    ),
    path(
        "postings/add",
        views.AddPostingsView.as_view(),
        name="add_postings",
    ),
]
