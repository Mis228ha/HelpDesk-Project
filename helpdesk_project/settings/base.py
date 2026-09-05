"""
Общие (базовые) настройки Django для проекта helpdesk_project.

Настройки, специфичные для окружения, находятся в:
- dev.py  — для локальной разработки (DEBUG=True, SQLite)
- prod.py — для продакшена (DEBUG=False, PostgreSQL и т.д.)

Секреты и параметры окружения читаются из файла .env в корне проекта
с помощью django-environ.
"""

from pathlib import Path

import environ

# BASE_DIR указывает на корень репозитория (где лежит manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# --- Инициализация django-environ ---------------------------------------
env = environ.Env(
    DEBUG=(bool, False),
)

# Читаем .env из корня проекта, если файл существует.
# В реальном проекте .env НЕ должен попадать в git (см. .gitignore).
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(env_file)


# --- Безопасность ---------------------------------------------------------
# SECRET_KEY и ALLOWED_HOSTS переопределяются в dev.py / prod.py,
# но значения по умолчанию берутся из .env, если он есть.
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="django-insecure-change-me-in-env-file-before-production",
)


# --- Приложения -------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "crispy_forms",
]

LOCAL_APPS = [
    "accounts",
    "tickets",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "helpdesk_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "helpdesk_project.wsgi.application"
ASGI_APPLICATION = "helpdesk_project.asgi.application"


# --- Валидация паролей ------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# --- Интернационализация -----------------------------------------------------
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True


# --- Статика и медиа ----------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --- django-crispy-forms -------------------------------------------------
# Собственный (не Bootstrap) шаблон-пак под чистую вёрстку проекта.
CRISPY_ALLOWED_TEMPLATE_PACKS = "custom"
CRISPY_TEMPLATE_PACK = "custom"

# Куда перенаправлять после логина/логаута (используется в accounts).
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "tickets:ticket_list"
LOGOUT_REDIRECT_URL = "accounts:login"
