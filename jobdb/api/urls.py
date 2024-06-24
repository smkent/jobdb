from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework import routers

from . import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"companies", views.CompanyViewSet)
router.register(
    r"companies/by_name", views.CompanyByNameViewSet, "company-by-name"
)
router.register(r"postings", views.PostingViewSet)
router.register(
    r"postings/by_url", views.PostingByURLViewSet, "posting-by-url"
)
router.register(r"applications", views.ApplicationViewSet)
router.register(
    r"applications/by_url", views.ApplicationByURLViewSet, "application-by-url"
)

urlpatterns = [
    path("", include(router.urls)),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "docs/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
]
