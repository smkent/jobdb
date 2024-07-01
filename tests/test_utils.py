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
        ),
        pytest.param(
            (
                "https://jobs.ashbyhq.com/rula"
                "/a86695b3-6dce-4ff7-828e-c7d5781fe6b5"
                "?locationId=d8ccc202-4d14-4fba-a9a5-667fe66dec77"
            ),
            (
                "https://jobs.ashbyhq.com/rula"
                "/a86695b3-6dce-4ff7-828e-c7d5781fe6b5"
            ),
            id="ashby",
        ),
        pytest.param(
            (
                "https://jobs.lever.co/aledade"
                "/c50ffde9-0a11-49b2-9703-c0908761ca1e"
                "?source=LinkedIn"
            ),
            (
                "https://jobs.lever.co/aledade"
                "/c50ffde9-0a11-49b2-9703-c0908761ca1e"
            ),
            id="lever",
        ),
        pytest.param("example.com", "https://example.com", id="bare_domain"),
        pytest.param(
            (
                "jobs.lever.co/aledade"
                "/c50ffde9-0a11-49b2-9703-c0908761ca1e"
                "?source=LinkedIn"
            ),
            (
                "https://jobs.lever.co/aledade"
                "/c50ffde9-0a11-49b2-9703-c0908761ca1e"
            ),
            id="lever_bare_url",
        ),
    ],
)
def test_normalize_posting_url(url: str, expected_result: str) -> None:
    assert normalize_posting_url(url) == expected_result
