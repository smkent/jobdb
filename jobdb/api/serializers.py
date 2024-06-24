from typing import Any

from rest_framework.serializers import HyperlinkedModelSerializer

from ..main.models import Application, Company, Posting


class CompanySerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Company
        fields = [
            "pk",
            "link",
            "name",
            "url",
            "careers_url",
            "hq",
            "employees_est",
            "employees_est_source",
            "how_found",
            "notes",
        ]


class PostingSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Posting
        fields = [
            "pk",
            "link",
            "company",
            "title",
            "url",
            "closed",
            "closed_note",
            "location",
            "wa_jurisdiction",
            "notes",
        ]


class ApplicationSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Application
        fields = [
            "pk",
            "link",
            "posting",
            "bona_fide",
            "applied",
            "reported",
            "notes",
        ]

    def create(self, validated_data: dict[str, Any]) -> Application:
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)  # type: ignore
