import re
from typing import Any
from urllib.parse import ParseResult, urlparse, urlunparse


def normalize_posting_url(url: str) -> str:
    bits = urlparse(url)

    def r(u: ParseResult, **kw: Any) -> ParseResult:
        return u._replace(**kw)

    if bits.netloc in {"linkedin.com", "www.linkedin.com"} and re.match(
        r"\/jobs\/view\/[0-9]+\/?", bits.path
    ):
        if not bits.path.endswith("/"):
            bits = r(bits, path=bits.path + "/")
        bits = r(bits, query="")
    return urlunparse(bits)
