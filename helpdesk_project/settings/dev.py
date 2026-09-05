"""
Настройки для локальной разработки.

Запуск: DJANGO_SETTINGS_MODULE=helpdesk_project.settings.dev
(значение по умолчанию, см. manage.py)

Используется SQLite — не требует установки СУБД, отлично подходит
для разработки и тестов. PostgreSQL подключается позже в prod.py.
"""

from .base import *  # noqa: F401,F403
from .base import BASE_DIR, env

DEBUG = env.bool("DJANGO_DEBUG", default=True)

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])


# --- База данных: SQLite для разработки -------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# --- Почта: в консоль, чтобы не настраивать SMTP при разработке -------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Дополнительные удобства для разработки
INTERNAL_IPS = ["127.0.0.1"]
