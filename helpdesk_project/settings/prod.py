"""
Настройки для продакшена.

Запуск: DJANGO_SETTINGS_MODULE=helpdesk_project.settings.prod

ВНИМАНИЕ:
- DEBUG всегда False.
- SECRET_KEY, ALLOWED_HOSTS и параметры PostgreSQL (DB_NAME, DB_USER,
  DB_PASSWORD, DB_HOST, DB_PORT) обязательно должны быть заданы через
  переменные окружения (.env на сервере или переменные CI/CD),
  никаких значений по умолчанию для продакшена здесь нет.
- Подключение к базе описано в base.py (общее для dev и prod).
  В продакшене USE_SQLITE должен быть False (значение по умолчанию).
"""

from .base import *  # noqa: F401,F403
from .base import env

DEBUG = False

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")  # без значения по умолчанию

SECRET_KEY = env("DJANGO_SECRET_KEY")  # обязателен в продакшене


# --- Безопасность для продакшена -----------------------------------------
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("DJANGO_SECURE_HSTS_SECONDS", default=3600)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# --- Почта ------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")