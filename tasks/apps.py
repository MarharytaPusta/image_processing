from django.apps import AppConfig


class TasksConfig(AppConfig):
    name = 'tasks'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        from .models import ImageTask

        try:
            zombie_tasks = ImageTask.objects.filter(status='processing')
            zombie_tasks.update(status='failed')
        except Exception:
            pass