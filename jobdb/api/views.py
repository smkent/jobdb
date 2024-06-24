from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend  # type: ignore
from drf_link_header_pagination import (  # type: ignore
    LinkHeaderLimitOffsetPagination,
)
from rest_framework.authentication import SessionAuthentication
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from ..main.models import Application, Company, Posting
from . import serializers
from .auth import APIKeyAuthentication


class APIViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, APIKeyAuthentication]
    filter_backends = [DjangoFilterBackend]
    pagination_class = LinkHeaderLimitOffsetPagination


class BaseCompanyViewSet(APIViewSet):
    queryset = Company.objects.all().order_by("name")
    serializer_class = serializers.CompanySerializer


class CompanyViewSet(BaseCompanyViewSet, ModelViewSet):
    pass


class CompanyByNameViewSet(BaseCompanyViewSet, RetrieveModelMixin):
    lookup_field = "name"


class BasePostingViewSet(APIViewSet):
    queryset = Posting.objects.all().order_by("company__name", "title", "url")
    serializer_class = serializers.PostingSerializer
    filterset_fields = ["company__name"]


class PostingViewSet(BasePostingViewSet, ModelViewSet):
    pass


class PostingByURLViewSet(BasePostingViewSet, RetrieveModelMixin):
    lookup_field = "url"
    lookup_value_regex = ".*"


class BaseApplicationViewSet(APIViewSet):
    queryset = Application.objects.all().order_by(
        "posting__company__name", "posting__title", "posting__url"
    )
    serializer_class = serializers.ApplicationSerializer
    filterset_fields = ["posting__company__name", "bona_fide"]

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(user=self.request.user)


class ApplicationViewSet(BaseApplicationViewSet, ModelViewSet):
    pass


class ApplicationByURLViewSet(BaseApplicationViewSet, RetrieveModelMixin):
    lookup_field = "posting__url"
    lookup_value_regex = ".*"
