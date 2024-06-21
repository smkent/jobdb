from django.contrib.admin import ModelAdmin, site
from django.db.models.query import QuerySet
from django.http import HttpRequest

from .models import Application, Company, Posting, User


class PostingAdmin(ModelAdmin):
    list_filter = ["company__name"]


class ApplicationAdmin(ModelAdmin):
    list_filter = ["bona_fide"]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = super().get_queryset(request)
        return qs.filter(user=request.user)


site.register(User)
site.register(Company)
site.register(Posting, PostingAdmin)
site.register(Application, ApplicationAdmin)
