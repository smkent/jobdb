import pytest

from jobdb.main.models import Company, User
from jobdb.main.query import (
    leaderboard_application_companies,
    posting_queue_set,
)


@pytest.mark.parametrize(
    ["username", "expected_queue"], [("luke", 0), ("solo", 1), ("vader", 2)]
)
def test_posting_with_applications(username: str, expected_queue: int) -> None:
    user = User.objects.get(username=username)
    assert (
        posting_queue_set(user=user).filter(company__name="Initech").count()
        == expected_queue
    )


def test_companies_with_applications() -> None:
    Company.objects.create(
        name="Foo, Inc",
        hq="Nowhere",
        employees_est="15",
        employees_est_source="LinkedIn",
        url="https://example.com/1",
        careers_url="https://example.com/1/1",
    )
    results = {
        row["company"]: row["application_count"]
        for row in leaderboard_application_companies().values(
            "company", "application_count"
        )
    }
    assert results == {"Initech": 6, "Initrode": 1}
