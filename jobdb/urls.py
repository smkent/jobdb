from django.contrib.admin import site as admin_site
from django.urls import include, path

from .admin import personal_admin_site

urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin_site.urls),
    path("portal/", personal_admin_site.urls),
    path("api/", include("jobdb.api.urls")),
    path("", include("jobdb.main.urls")),
]
