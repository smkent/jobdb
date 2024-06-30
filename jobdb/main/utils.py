import re
from typing import Any
from urllib.parse import ParseResult, urlparse, urlunparse


def normalize_posting_url(url: str) -> str:
    bits = urlparse(url.strip())

    def r(u: ParseResult, **kw: Any) -> ParseResult:
        return u._replace(**kw)

    if bits.netloc in {"linkedin.com", "www.linkedin.com"} and re.match(
        r"\/jobs\/view\/[0-9]+\/?", bits.path
    ):
        if not bits.path.endswith("/"):
            bits = r(bits, path=bits.path + "/")
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
