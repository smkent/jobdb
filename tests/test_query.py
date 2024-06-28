import pytest

from jobdb.main.models import User
from jobdb.main.query import posting_queue_set


@pytest.mark.django_db
@pytest.mark.parametrize(
    ["username", "expected_queue"], [("luke", 0), ("solo", 1), ("vader", 2)]
)
def test_posting_with_applications(username: str, expected_queue: int) -> None:
    user = User.objects.get(username=username)
    assert (
        posting_queue_set(user=user).filter(company__name="Initech").count()
        == expected_queue
    )
