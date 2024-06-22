from django.contrib.admin.apps import AdminConfig as BaseAdminConfig


class AdminConfig(BaseAdminConfig):
    default_site = "jobdb.admin.AdminSite"


class SecondAdminConfig(AdminConfig):
    default_site = "jobdb.admin.PersonalAdminSite"
