#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from util.lwgk import LWGMKNN
from sklearn.metrics.pairwise import euclidean_distances
#from django.core.management import execute_from_command_line
venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv', 'Lib', 'site-packages')

# Add the virtual environment's site-packages to the system path
sys.path.append(venv_path)


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'We_CDSS.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "We_CDSS.settings")  # Replace 'myproject' with your actual project name
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Bind the app to the correct port
    port = os.getenv("PORT", "8000")
    execute_from_command_line([sys.argv[0], "runserver", f"0.0.0.0:{port}"])
