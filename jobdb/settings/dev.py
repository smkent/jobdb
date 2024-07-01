from .base import *  # noqa
from .base import BASE_DIR
from .email import MsmtpConfig

ALLOWED_HOSTS = [".localhost", "127.0.0.1", "[::1]"]
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = (  # nosec
    "django-insecure-4!5k$k1q9!v5q2@f9i_gn!m@e8+uez3s0v-zn*nf&0f1_ync(5"
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

msmtp = MsmtpConfig()
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = msmtp.host
EMAIL_PORT = msmtp.port
EMAIL_USE_TLS = msmtp.use_tls
EMAIL_HOST_USER = msmtp.host_user
EMAIL_HOST_PASSWORD = msmtp.host_password
