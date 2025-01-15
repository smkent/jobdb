import re
from contextlib import suppress
from itertools import islice
from typing import Any
from collections.abc import Iterator
from urllib.parse import ParseResult, urlparse, urlunparse
from uuid import UUID


def normalize_posting_url(url: str) -> str:
    def r(u: ParseResult, **kw: Any) -> ParseResult:
        return u._replace(**kw)

    url = url.strip()
    if not url:
        return ""
    if not (url.startswith("http:" + "//") or url.startswith("https:" + "//")):
        url = "https:" f"//{url}"
    bits = urlparse(url.strip())
    if bits.netloc in {"linkedin.com", "www.linkedin.com"} and re.match(
        r"\/jobs\/view\/[0-9]+\/?", bits.path
    ):
        if not bits.path.endswith("/"):
            bits = r(bits, path=bits.path + "/")
        bits = r(bits, query="")
    if bits.netloc in {"jobs.ashbyhq.com", "jobs.lever.co"}:
        with suppress(ValueError):
            UUID(bits.path.rstrip("/").rsplit("/", 1)[-1])
            bits = r(bits, query="")
    return urlunparse(bits)


def url_to_text(url: str) -> str:
    netloc_max = 25
    path_max = 27
    url_parts = urlparse(url)
    split_data = url_parts.path + (
        "?" + url_parts.query if url_parts.query else ""
    )
    bits = split_data.rsplit("/", maxsplit=2)[-2:]
    path_bits = ("/" + "/".join([bit for bit in bits if bit]))[-path_max:]
    netloc_bits = (
        url_parts.netloc[: (netloc_max - 3)] + "[...]"
        if len(url_parts.netloc) > netloc_max
        else url_parts.netloc
    )
    if path_bits == split_data:
        return f"{netloc_bits}{path_bits}"
    else:
        return f"{netloc_bits}/[...]{path_bits}"


def batched(iterable: Any, n: int) -> Iterator[Any]:
    it = iter(iterable)
    while True:
        if not (batch := list(islice(it, n))):
            return
        yield batch
