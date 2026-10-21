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

# --- Доступ по локальной сети (LAN) ------------------------------------------
# "*" разрешает обращаться к сайту по любому хосту/IP, поэтому его можно открыть
# с других устройств: http://<IP-вашего-компьютера>:8000 (см. README,
# раздел «Доступ по локальной сети»).
#
# ТОЛЬКО ДЛЯ РАЗРАБОТКИ! В продакшене (prod.py) ALLOWED_HOSTS берётся из
# переменной окружения DJANGO_ALLOWED_HOSTS — там нужно перечислить
# конкретные домены/IP, а не "*".
#
# Вместо "*" можно указать конкретные адреса, например:
# ALLOWED_HOSTS = ["localhost", "127.0.0.1", "192.168.1.50"]
ALLOWED_HOSTS = ["*"]

# CSRF_TRUSTED_ORIGINS (необязательно). При заходе по IP в локальной сети формы
# обычно работают и без этой настройки (Django сверяет Origin с Host запроса).
# Если при отправке формы появляется ошибка «CSRF verification failed» —
# например, при доступе через прокси/туннель, — перечислите адреса (СО схемой
# http:// и портом) в .env через запятую:
#   DJANGO_CSRF_TRUSTED_ORIGINS=http://192.168.1.50:8000,http://192.168.1.51:8000
# Маски вида 192.168.*.* Django не поддерживает — адреса указываются явно.
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])


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