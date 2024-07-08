from typing import Any

from rest_framework.serializers import (
    BooleanField,
    CharField,
    HyperlinkedModelSerializer,
    HyperlinkedRelatedField,
    IntegerField,
)

from ..main.models import Application, Company, Posting, User


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = [
            "pk",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "linkedin",
        ]
        extra_kwargs = {"username": {"read_only": True}}


class CompanySerializer(HyperlinkedModelSerializer):
    num_postings = IntegerField(source="posting_count", read_only=True)

    class Meta:
        model = Company
        fields = [
            "pk",
            "link",
            "name",
            "url",
            "careers_url",
            "careers_urls",
            "hq",
            "num_postings",
            "employees_est",
            "employees_est_source",
            "how_found",
            "notes",
        ]


class PostingSerializer(HyperlinkedModelSerializer):
    company_name = CharField(source="company.name", read_only=True)

    class Meta:
        model = Posting
        fields = [
            "pk",
            "link",
            "company",
            "company_name",
            "title",
            "url",
            "job_board_urls",
            "closed",
            "closed_note",
            "in_wa",
            "location",
            "wa_jurisdiction",
            "notes",
        ]


class ApplicationSerializer(HyperlinkedModelSerializer):
    company: HyperlinkedRelatedField = HyperlinkedRelatedField(
        source="posting.company", read_only=True, view_name="company-detail"
    )
    company_name = CharField(source="posting.company.name", read_only=True)
    posting_url = CharField(source="posting.url", read_only=True)
    posting_in_wa = BooleanField(source="posting.in_wa", read_only=True)

    class Meta:
        model = Application
        fields = [
            "pk",
            "link",
            "company",
            "company_name",
            "posting",
            "posting_url",
            "posting_in_wa",
            "bona_fide",
            "applied",
            "reported",
            "notes",
        ]

    def create(self, validated_data: dict[str, Any]) -> Application:
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)  # type: ignore
