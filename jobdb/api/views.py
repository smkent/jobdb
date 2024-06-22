from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend  # type: ignore
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from ..main.models import Application, Company, Posting
from . import serializers
from .auth import APIKeyAuthentication


class APIModelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, APIKeyAuthentication]
    filter_backends = [DjangoFilterBackend]


class CompanyViewSet(APIModelViewSet):
    queryset = Company.objects.all().order_by("name")
    serializer_class = serializers.CompanySerializer


class PostingViewSet(APIModelViewSet):
    queryset = Posting.objects.all().order_by("company__name", "title", "url")
    serializer_class = serializers.PostingSerializer
    filterset_fields = ["company__name"]


class ApplicationViewSet(APIModelViewSet):
    queryset = Application.objects.all().order_by(
        "posting__company__name", "posting__title", "posting__url"
    )
    serializer_class = serializers.ApplicationSerializer
    filterset_fields = ["posting__company__name", "bona_fide"]

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(user=self.request.user)
