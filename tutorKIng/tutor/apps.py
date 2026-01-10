from django.apps import AppConfig
from django.core.signals import request_started
from django.dispatch import receiver

class TutorConfig(AppConfig):
    name = 'tutor'  # Name of the app as registered in INSTALLED_APPS

    def ready(self):
        # Import the scheduler module when the app is ready
        from . import scheduler

        @receiver(request_started)  # Connect to Django's signal triggered on every request
        def start_scheduler(sender, **kwargs):
            """
            Starts the background scheduler on the first incoming request.
            This avoids multiple scheduler threads during dev server reloads.
            """
            scheduler.start()