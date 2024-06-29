import pytest

from jobdb.main.utils import normalize_posting_url


@pytest.mark.parametrize(
    ["url", "expected_result"],
    [
        pytest.param(
            (
                "https://www.linkedin.com/jobs/view/3943736060/"
                "?alternateChannel=search"
                "&refId=Ok%2BKJCffiXY5f1tWg%2Blafw%3D%3D"
                "&trackingId=6RnLLeJMFugca9mXUTWCnw%3D%3D"
                "&trk=d_flagship3_search_srp_jobs"
                "&lipi=urn%3Ali%3Apage%3Ad_flagship3_search_srp_jobs"
                "%3BVwCkjGvbSi%2B8rS0kyv1ITw%3D%3D"
            ),
            "https://www.linkedin.com/jobs/view/3943736060/",
            id="linkedin",
        )
    ],
)
def test_normalize_posting_url(url: str, expected_result: str) -> None:
    assert normalize_posting_url(url) == expected_result
