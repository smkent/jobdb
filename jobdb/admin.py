from django.contrib.admin import AdminSite as BaseAdminSite
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpRequest


class AdminSite(BaseAdminSite):
    site_header = "Autojob administration"
    site_title = "Autojob admin"


class PersonalAdminSite(BaseAdminSite):
    site_header = "Autojob"
    site_title = "Autojob portal"
    site_url = None
    index_title = "Home"

    login_form = AuthenticationForm

    def has_permission(self, request: HttpRequest) -> bool:
        return bool(request.user.is_active)


personal_admin_site = PersonalAdminSite("personal")
