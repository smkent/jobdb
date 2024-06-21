from django.contrib.admin import ModelAdmin, site

from .models import Application, Company, Posting, User


class PostingAdmin(ModelAdmin):
    list_filter = ["company__name"]


class ApplicationAdmin(ModelAdmin):
    list_filter = ["bona_fide"]


site.register(User)
site.register(Company)
site.register(Posting, PostingAdmin)
site.register(Application, ApplicationAdmin)
