from django.contrib.admin import ModelAdmin, site

from ..admin import personal_admin_site
from .models import Application, Company, Posting, User


class PostingAdmin(ModelAdmin):
    list_filter = ["company__name"]


class ApplicationAdmin(ModelAdmin):
    list_filter = ["bona_fide"]


site.register(Posting, PostingAdmin)
site.register(Application, ApplicationAdmin)
site.register(Company)
site.register(User)
personal_admin_site.register(Company)
