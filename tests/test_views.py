from django.test.client import Client
from django.urls import reverse

from jobdb.main.models import User


def test_index_view_unauthorized(client: Client) -> None:
    response = client.get(reverse("index"))
    assert response.status_code == 302
    assert response.url == (  # type: ignore
        reverse("login") + "?next=" + reverse("index")
    )


def test_index_view(client: Client) -> None:
    client.force_login(User.objects.get(username="luke"))
    response = client.get(reverse("index"))
    assert response.status_code == 200
