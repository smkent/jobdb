#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import subprocess
import sys


def main() -> None:
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jobdb.settings")
    try:
        from django.core.management import (  # type: ignore
            execute_from_command_line,
        )
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    if os.environ.get("VIRTUAL_ENV"):
        main()
    else:
        subprocess.run(["poetry", "run", "python"] + sys.argv)  # nosec
