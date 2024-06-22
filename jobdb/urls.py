from django.contrib.admin import site as admin_site
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path

from .admin import personal_admin_site

urlpatterns = [
    path("admin/", admin_site.urls),
    path("portal/", personal_admin_site.urls),
    path(
        "login/", LoginView.as_view(template_name="login.html"), name="login"
    ),
    path("logout/", LogoutView.as_view()),
    path("", include("jobdb.main.urls")),
]
