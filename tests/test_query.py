import pytest

from jobdb.main.models import User
from jobdb.main.query import (
    company_posting_queue_set,
    posting_queue_companies_count,
    posting_queue_set,
    user_companies_leaderboard,
)


@pytest.mark.parametrize(
    ["username", "expected_queue"], [("luke", 0), ("solo", 2), ("vader", 3)]
)
def test_posting_with_applications(username: str, expected_queue: int) -> None:
    user = User.objects.get(username=username)
    assert (
        posting_queue_set(user=user).filter(company__name="Initech").count()
        == expected_queue
    )


@pytest.mark.parametrize(
    ["username", "expected_queue"],
    [
        ("luke", []),
        (
            "solo",
            [
                {
                    "company__name": "Initrode",
                    "pk": 20,
                    "title": "Executive Michael Bolton",
                }
            ],
        ),
        (
            "vader",
            [
                {
                    "company__name": "Initech",
                    "pk": 13,
                    "title": "General Major Webelos",
                },
                {
                    "company__name": "Initrode",
                    "pk": 20,
                    "title": "Executive Michael Bolton",
                },
            ],
        ),
    ],
)
def test_posting_queue(username: str, expected_queue: int) -> None:
    user = User.objects.get(username=username)
    assert (
        list(
            company_posting_queue_set(user=user).values(
                "pk", "company__name", "title"
            )
        )
        == expected_queue
    )


@pytest.mark.parametrize(
    ["username", "expected_counts"],
    [
        ("luke", []),
        ("solo", [("Initrode", 1)]),
        ("vader", [("Initech", 1), ("Initrode", 1)]),
    ],
)
def test_posting_queue_companies_count(
    username: str, expected_counts: list[tuple[str, int]]
) -> None:
    user = User.objects.get(username=username)
    response = posting_queue_companies_count(user).values("name", "count")
    assert list(response.values_list("name", "count")) == expected_counts


def test_user_companies_leaderboard() -> None:
    response = user_companies_leaderboard()
    assert list(response) == [
        {"user__first_name": "Luke", "user__username": "luke", "count": 2},
        {"user__first_name": "Han", "user__username": "solo", "count": 1},
        {"user__first_name": "Darth", "user__username": "vader", "count": 1},
    ]
