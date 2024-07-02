import time
from argparse import ArgumentParser
from typing import Any
from urllib.parse import urlparse

import requests
from django.core.management.base import BaseCommand
from django.db.models import QuerySet
from django.db.models.functions import Lower
from django.utils import timezone

from jobdb.main.models import Posting

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        " AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/126.0.0.0 Safari/537.36"
    )
}


class Command(BaseCommand):
    help = "Checks for closed posting URLs"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "-c",
            "--company",
            dest="companies",
            metavar="company",
            action="append",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        queryset = Posting.objects.filter(closed=None)
        if company_names := options.get("companies"):
            queryset = queryset.annotate(
                company_name_lower=Lower("company__name")
            ).filter(company_name_lower__in=[n.lower() for n in company_names])
        self.run(queryset)
        self.stdout.write(self.style.SUCCESS("Did the thing"))

    def run(self, postings: QuerySet) -> None:
        for posting in postings.all():
            url_bits = urlparse(posting.url)
            # Skip LinkedIn URLs, which can redirect to the login page
            if url_bits.netloc in {"linkedin.com", "www.linkedin.com"}:
                continue
            self.check_posting(posting)

    def check_posting(self, posting: Posting) -> None:
        response = requests.head(
            posting.url,
            allow_redirects=False,
            timeout=3,
            headers=HEADERS.copy(),
        )
        if 300 <= response.status_code <= 399:
            dest = response.headers.get("Location")
            posting.closed = timezone.now()
            posting.closed_note = (
                "Closed automatically by check_posting_urls command"
            )
            posting.save()
            print(f"Closed {posting.url} [redirected to {dest}]")
        else:
            print(f"Normal response: {posting.url}")
        time.sleep(0.5)
