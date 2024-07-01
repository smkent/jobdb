import os
from pathlib import Path


class EnvValue:
    def _raw(self, var: str) -> str | None:
        for try_file in [var, f"{var}_FILE"]:
            if (p := Path(try_file)).is_file():
                return p.read_text().strip()
        return os.environ.get(var)

    def bool(self, var: str, default: str = "") -> bool:
        return (self._raw(var) or "").lower() in {"true", "yes", "1"}

    def integer(self, var: str, default: int = 0) -> int:
        value = self._raw(var)
        return default if value is None else int(value)

    def string(self, var: str, default: str = "") -> str:
        return self._raw(var) or ""
