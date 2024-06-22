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
router.register(r"postings", views.PostingViewSet)
router.register(r"applications", views.ApplicationViewSet)

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
