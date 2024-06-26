from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "companies", views.CompanyHTMxTableView.as_view(), name="company_htmx"
    ),
]
