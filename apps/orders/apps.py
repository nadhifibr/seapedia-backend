from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.orders'

    def ready(self):
        import os
        # Only start scheduler in the main process
        if os.environ.get('RUN_MAIN', None) == 'true':
            from . import jobs
            jobs.start_scheduler()
