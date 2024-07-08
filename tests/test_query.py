import pytest

from jobdb.main.models import User
from jobdb.main.query import posting_queue_companies_count, posting_queue_set


@pytest.mark.parametrize(
    ["username", "expected_queue"], [("luke", 0), ("solo", 1), ("vader", 2)]
)
def test_posting_with_applications(username: str, expected_queue: int) -> None:
    user = User.objects.get(username=username)
    assert (
        posting_queue_set(user=user).filter(company__name="Initech").count()
        == expected_queue
    )


@pytest.mark.parametrize(
    ["username", "expected_counts"],
    [
        ("luke", []),
        ("solo", [("Initech", 1), ("Initrode", 1)]),
        ("vader", [("Initech", 2), ("Initrode", 1)]),
    ],
)
def test_posting_queue_companies_count(
    username: str, expected_counts: list[tuple[str, int]]
) -> None:
    user = User.objects.get(username=username)
    response = posting_queue_companies_count(user).values("name", "count")
    assert list(response.values_list("name", "count")) == expected_counts
