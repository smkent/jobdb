from .base import *  # noqa

ALLOWED_HOSTS = ["*"]
DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "jobdb",
        "USER": "jobdb",
        "PASSWORD": "jobdb",
        "HOST": "db",
        "PORT": 5432,
    }
}
