from django.db.models import QuerySet
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from ..main.models import Application, Company, Posting
from . import serializers
from .auth import APIKeyAuthentication


class APIModelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [APIKeyAuthentication]


class CompanyViewSet(APIModelViewSet):
    """
    API endpoint that allows companies to be viewed or edited.
    """

    queryset = Company.objects.all().order_by("name")
    serializer_class = serializers.CompanySerializer


class PostingViewSet(APIModelViewSet):
    """
    API endpoint that allows companies to be viewed or edited.
    """

    queryset = Posting.objects.all().order_by("company__name", "title", "url")
    serializer_class = serializers.PostingSerializer


class ApplicationViewSet(APIModelViewSet):
    """
    API endpoint that allows companies to be viewed or edited.
    """

    queryset = Application.objects.all().order_by(
        "posting__company__name", "posting__title", "posting__url"
    )
    serializer_class = serializers.ApplicationSerializer

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(user=self.request.user)
