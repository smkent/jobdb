from django.urls import reverse
from rest_framework.test import APIClient


def test_api_unauthorized() -> None:
    api_client = APIClient()
    assert api_client.get(reverse("api-root")).status_code == 401


def test_api_invalid_apikey() -> None:
    api_client = APIClient()
    api_client.credentials(HTTP_AUTHORIZATION="Bearer invalid-key")
    assert api_client.get(reverse("api-root")).status_code == 401


def test_api_root(api_client: APIClient) -> None:
    assert api_client.get(reverse("api-root")).status_code == 200


def test_api_me(api_client: APIClient) -> None:
    response = api_client.get(reverse("api-me"))
    assert response.status_code == 200
    assert response.json() == {
        "pk": 1138,
        "username": "luke",
        "email": "",
        "first_name": "Luke",
        "last_name": "Skywalker",
        "linkedin": "https://linkedin.com/in/luke.skywalker",
        "phone": "",
    }
