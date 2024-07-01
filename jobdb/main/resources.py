from django.db.models import QuerySet
from import_export.resources import ModelResource  # type: ignore

from .models import User


class UserResource(ModelResource):
    class Meta:
        model = User
        exclude = ["password"]

    def get_queryset(self) -> QuerySet:
        return User.objects.exclude(username="admin")
