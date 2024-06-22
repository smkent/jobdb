from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"companies", views.CompanyViewSet)
router.register(r"postings", views.PostingViewSet)
router.register(r"applications", views.ApplicationViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
