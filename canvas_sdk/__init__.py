import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

if "mypy" not in sys.argv[0]:
    import django

    django.setup()


__exports__ = ()
