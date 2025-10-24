"""
WSGI config for cacaoscan project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')

application = get_wsgi_application()
