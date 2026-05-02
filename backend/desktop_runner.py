import os
import sys
from pathlib import Path


def main() -> None:
    backend_root = Path(__file__).resolve().parent
    os.chdir(backend_root)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    os.environ.setdefault("BACKSTAB_DESKTOP", "1")

    from django.core.management import execute_from_command_line

    execute_from_command_line([sys.argv[0], "migrate", "--noinput"])
    execute_from_command_line(
        [sys.argv[0], "runserver", "127.0.0.1:8000", "--noreload"]
    )


if __name__ == "__main__":
    main()
