from rest_framework.authentication import TokenAuthentication

from ..main.models import APIKey


class APIKeyAuthentication(TokenAuthentication):
    keyword = "Bearer"
    model = APIKey
