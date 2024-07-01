from contextlib import suppress
from typing import Any, Sequence

from django.db.models import Model, QuerySet
from import_export.fields import Field  # type: ignore
from import_export.resources import ModelResource  # type: ignore

from .models import Application, Company, Posting, User


class ModelResourceWithoutPK(ModelResource):
    def get_export_fields(self) -> Sequence[Field]:
        fields = super().get_export_fields()
        return [f for f in fields if f.attribute not in {"id"}]

    def before_import_row(self, row: dict[str, Any], **kwargs: Any) -> Any:
        with suppress(self._meta.model.DoesNotExist):
            row["id"] = self.get_object_from_row(row).pk
        return super().before_import_row(row, **kwargs)

    def get_object_from_row(self, row: dict[str, Any]) -> Model:
        raise NotImplementedError


class UserResource(ModelResourceWithoutPK):
    class Meta:
        model = User
        exclude = ["password"]

    def get_queryset(self) -> QuerySet:
        return User.objects.exclude(username="admin")

    def get_object_from_row(self, row: dict[str, Any]) -> Model:
        return User.objects.get(username=row["username"])


class CompanyResource(ModelResourceWithoutPK):
    def get_object_from_row(self, row: dict[str, Any]) -> Model:
        return Company.objects.get(name=row["name"])  # type: ignore

    class Meta:
        model = Company


class PostingResource(ModelResourceWithoutPK):
    company_name = Field(attribute="company__name", column_name="company_name")

    def get_object_from_row(self, row: dict[str, Any]) -> Model:
        return Posting.objects.get(url=row["url"])  # type: ignore

    def before_import_row(self, row: dict[str, Any], **kwargs: Any) -> Any:
        row["company"] = Company.objects.get(name=row["company_name"]).pk
        return super().before_import_row(row, **kwargs)

    def get_export_fields(self) -> Sequence[Field]:
        fields = super().get_export_fields()
        return [f for f in fields if f.attribute not in {"company_id"}]

    class Meta:
        model = Posting


class ApplicationResource(ModelResourceWithoutPK):
    username = Field(attribute="user__username", column_name="username")
    posting_url = Field(attribute="posting__url", column_name="posting_url")
    import_id_fields = ["user", "posting"]

    def get_object_from_row(self, row: dict[str, Any]) -> Model:
        return Application.objects.get(
            user__pk=row["user"], posting__pk=row["posting"]
        )

    def before_import_row(self, row: dict[str, Any], **kwargs: Any) -> Any:
        if not row.get("user") and (user_name := row.get("username")):
            row["user"] = User.objects.get(username=user_name).pk
        row["posting"] = Posting.objects.get(url=row["posting_url"]).pk
        return super().before_import_row(row, **kwargs)

    def get_export_fields(self) -> Sequence[Field]:
        fields = super().get_export_fields()
        return [
            f for f in fields if f.attribute not in {"user_id", "posting_id"}
        ]

    class Meta:
        model = Application


class UserApplicationResource(ApplicationResource):
    def __init__(self, *args: Any, user: User | None = None, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.user = user

    class Meta:
        model = Application

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(user=self.user)  # type: ignore

    def before_import_row(self, row: dict[str, Any], **kwargs: Any) -> Any:
        assert isinstance(self.user, User)
        row["user"] = self.user.pk
        return super().before_import_row(row, **kwargs)

    def get_export_fields(self) -> Sequence[Field]:
        fields = super().get_export_fields()
        return [f for f in fields if f.attribute not in {"user__username"}]
