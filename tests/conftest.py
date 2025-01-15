from collections.abc import Iterator

import pytest
from django.core.management import call_command
from pytest_django import DjangoDbBlocker
from rest_framework.test import APIClient

from jobdb.main.models import APIKey, User


@pytest.fixture(scope="session")
def django_db_setup(
    django_db_setup: None, django_db_blocker: DjangoDbBlocker
) -> None:
    with django_db_blocker.unblock():
        call_command("loaddata", "test-data.yaml")


@pytest.fixture(autouse=True)
def enable_db_access(db: None) -> None:
    pass


@pytest.fixture
def api_client() -> Iterator[APIClient]:
    user = User.objects.get(username="luke")
    api_client = APIClient()
    api_client.credentials(
        HTTP_AUTHORIZATION="Bearer "
        + APIKey.objects.filter(user=user).first().key
    )
    yield api_client
