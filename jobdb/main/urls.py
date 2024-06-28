from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path(
        "companies", views.CompanyHTMxTableView.as_view(), name="company_htmx"
    ),
    path(
        "postings", views.PostingHTMxTableView.as_view(), name="posting_htmx"
    ),
    path(
        "applications",
        views.ApplicationHTMxTableView.as_view(),
        name="application_htmx",
    ),
    path("queue", views.QueueHTMxTableView.as_view(), name="queue_htmx"),
]
