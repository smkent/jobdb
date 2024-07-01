from contextlib import suppress
from typing import Any, Sequence

from django.db.models import QuerySet
from import_export.fields import Field  # type: ignore
from import_export.resources import ModelResource  # type: ignore

from .models import Application, Company, Posting, User


class UserResource(ModelResource):
    class Meta:
        model = User
        exclude = ["password"]

    def get_queryset(self) -> QuerySet:
        return User.objects.exclude(username="admin")


class ModelResourceWithoutPK(ModelResource):
    def get_export_fields(self) -> Sequence[Field]:
        fields = super().get_export_fields()
        return [f for f in fields if f.attribute not in {"id"}]


class CompanyResource(ModelResourceWithoutPK):
    def before_import_row(self, row: dict[str, Any], **kwargs: Any) -> Any:
        with suppress(Company.DoesNotExist):
            row["id"] = Company.objects.get(name=row["name"]).pk
        return super().before_import_row(row, **kwargs)

    class Meta:
        model = Company


class PostingResource(ModelResourceWithoutPK):
    def before_import_row(self, row: dict[str, Any], **kwargs: Any) -> Any:
        with suppress(Posting.DoesNotExist):
            row["id"] = Posting.objects.get(url=row["url"]).pk
        return super().before_import_row(row, **kwargs)

    class Meta:
        model = Posting


class UserApplicationResource(ModelResourceWithoutPK):
    def __init__(self, *args: Any, user: User | None = None, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.user = user

    class Meta:
        model = Application

    def get_export_fields(self) -> Sequence[Field]:
        fields = super().get_export_fields()
        return [f for f in fields if f.attribute not in {"user_id"}]

    def before_import_row(self, row: dict[str, Any], **kwargs: Any) -> Any:
        assert isinstance(self.user, User)
        row["user"] = self.user.pk
        row["id"] = None
        with suppress(Application.DoesNotExist):
            row["id"] = Application.objects.get(
                user__pk=self.user.pk, posting__pk=row["posting"]
            ).pk
        return super().before_import_row(row, **kwargs)

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(user=self.user)  # type: ignore
