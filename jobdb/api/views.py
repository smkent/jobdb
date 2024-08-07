from typing import Any

from django.db.models import QuerySet
from django.http.response import Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend  # type: ignore
from drf_link_header_pagination import (  # type: ignore
    LinkHeaderLimitOffsetPagination,
)
from drf_problems.exceptions import exception_handler  # type: ignore
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView as BaseAPIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from ..main.models import Application, Posting, User
from ..main.query import (
    companies_with_counts,
    company_posting_queue_set,
    posting_queue_set,
)
from . import serializers
from .auth import APIKeyAuthentication
from .filters import ApplicationFilter, CompanyFilter, PostingFilter


class APIPagination(LinkHeaderLimitOffsetPagination):
    default_limit = 10
    max_limit = 1000


class APIView(GenericAPIView, BaseAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, APIKeyAuthentication]


class APIViewSet(APIView, GenericViewSet):
    filter_backends = [DjangoFilterBackend]
    pagination_class = APIPagination

    def get_exception_handler(self) -> Any:
        return exception_handler


class MeView(APIViewSet, RetrieveModelMixin, UpdateModelMixin):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    def get_object(self) -> User:
        assert isinstance(self.request.user, User)
        return self.request.user


class BaseCompanyViewSet(APIViewSet):
    queryset = companies_with_counts().order_by("name")
    serializer_class = serializers.CompanySerializer


class CompanyViewSet(BaseCompanyViewSet, ModelViewSet):
    filterset_class = CompanyFilter


class CompanyByNameViewSet(BaseCompanyViewSet, RetrieveModelMixin):
    lookup_field = "name"


class BasePostingViewSet(APIViewSet):
    queryset = Posting.objects.all().order_by("company__name", "title", "url")
    serializer_class = serializers.PostingSerializer


class PostingViewSet(BasePostingViewSet, ModelViewSet):
    filterset_class = PostingFilter


class PostingByURLViewSet(BasePostingViewSet, RetrieveModelMixin):
    lookup_field = "url"
    lookup_value_regex = ".*"

    def get_object(self) -> Posting:
        try:
            return super().get_object()  # type: ignore
        except Http404:
            qs = self.get_queryset().by_url(self.kwargs["url"])  # type: ignore
            return get_object_or_404(qs)  # type: ignore


class FullPostingQueueViewSet(BasePostingViewSet, ListModelMixin):
    filterset_class = PostingFilter
    serializer_class = serializers.PostingSerializer

    def get_queryset(self) -> QuerySet:
        assert isinstance(self.request.user, User)
        return posting_queue_set(self.request.user, ordered=True)


class PostingQueueViewSet(FullPostingQueueViewSet):
    def get_queryset(self) -> QuerySet:
        assert isinstance(self.request.user, User)
        return company_posting_queue_set(self.request.user)


class BaseApplicationViewSet(APIViewSet):
    queryset = Application.objects.all().order_by(
        "posting__company__name", "posting__title", "posting__url"
    )
    serializer_class = serializers.ApplicationSerializer

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(user=self.request.user)


class ApplicationViewSet(BaseApplicationViewSet, ModelViewSet):
    filterset_class = ApplicationFilter


class ApplicationByURLViewSet(BaseApplicationViewSet, RetrieveModelMixin):
    lookup_field = "posting__url"
    lookup_value_regex = ".*"
