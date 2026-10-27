from django.apps import AppConfig


class TicketsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tickets'

    def ready(self):
        # Подключаем сигналы (удаление файлов вложений с диска).
        from . import signals  # noqa: F401