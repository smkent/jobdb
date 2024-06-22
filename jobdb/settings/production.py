import os

from django.utils.log import DEFAULT_LOGGING

from .base import *  # noqa
from .base import BASE_DIR

DEFAULT_LOGGING["handlers"]["console"]["filters"] = []

ALLOWED_HOSTS = ["*"]
DEBUG = False

SECRET_KEY = os.environ.get("SECRET_KEY")

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

STATIC_ROOT = BASE_DIR / "static"
