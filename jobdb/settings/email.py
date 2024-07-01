from dataclasses import dataclass, field
from pathlib import Path

from .env import EnvValue

_env = EnvValue()

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = _env.string("DJANGO_EMAIL_HOST")
EMAIL_PORT = _env.integer("DJANGO_EMAIL_PORT", 25)
EMAIL_USE_TLS = _env.bool("DJANGO_EMAIL_USE_TLS")
EMAIL_HOST_USER = _env.string("DJANGO_EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = _env.string("DJANGO_EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = _env.string(
    "DJANGO_DEFAULT_FROM_EMAIL", "jobdb@" + EMAIL_HOST
)


@dataclass
class MsmtpConfig:
    config_file = Path("~/.msmtprc").expanduser()
    host: str = ""
    port: int = 25
    use_tls: bool = False
    host_user: str = ""
    host_password: str = field(default="", repr=False)

    def __post_init__(self) -> None:
        if not self.config_file.is_file():
            return
        for line in self.config_file.read_text().splitlines():
            if not (line := line.strip().split("#", 1)[0].strip()):
                continue
            if " " not in line:
                continue
            key, value = line.split(" ", 1)
            if key.lower() == "host":
                self.host = value
            elif key.lower() == "port":
                self.port = int(value)
            elif key.lower() in {"tls", "tls_starttls"}:
                self.use_tls = value.lower() in {"on"}
            elif key.lower() == "user":
                self.host_user = value
            elif key.lower() == "password":
                self.host_password = value
