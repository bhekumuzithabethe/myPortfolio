"""
WSGI config for tutorKing project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
settings_module = "tutorKing.deployment" if 'WEBSITE_HOSTENAME' in os.environ else 'tutorKing.settings'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tutorKing.settings')
os.environ.setdefault('DJANGO_SETTING_MODULE', settings_module)

application = get_wsgi_application()
