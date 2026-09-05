# Helpdesk Project

Учебный/стартовый Django-проект службы поддержки: пользователи создают
заявки (tickets), заявки привязаны к автору (accounts — стандартная
модель пользователя Django).

## Стек

- Python 3.10, Django 4.2 (LTS)
- SQLite для разработки, заготовка под PostgreSQL для продакшена
- django-environ — настройки через `.env`
- django-crispy-forms — рендеринг форм, свой шаблон-пак `custom` (без Bootstrap)
- Вёрстка: чистые HTML/CSS, без фреймворков и JS

## Структура проекта

```
helpdesk_project/
├── manage.py
├── helpdesk_project/        # пакет настроек и корневой urls.py
│   ├── settings/
│   │   ├── base.py          # общие настройки
│   │   ├── dev.py           # разработка (SQLite, DEBUG=True)
│   │   └── prod.py          # продакшен (заготовка под PostgreSQL)
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/                 # регистрация, вход, выход
├── tickets/                   # модель Ticket, CRUD-заявки
├── templates/
│   ├── base.html              # header / nav / content / footer
│   ├── accounts/
│   ├── tickets/
│   └── custom/                 # свой шаблон-пак для django-crispy-forms
├── static/css/style.css        # вся вёрстка проекта
├── requirements.txt
├── .env.example
└── .gitignore
```

## Установка и запуск (локально)

Требуется Python 3.10.

```bash
# 1. Клонировать репозиторий и перейти в папку проекта
cd helpdesk_project

# 2. Создать и активировать виртуальное окружение
python3.10 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Настроить переменные окружения
cp .env.example .env
# при желании отредактировать .env (для разработки можно не менять)

# 5. Применить миграции
python manage.py migrate

# 6. Создать суперпользователя (для входа в /admin/)
python manage.py createsuperuser

# 7. Запустить сервер разработки
python manage.py runserver
```

По умолчанию используются настройки для разработки
(`helpdesk_project.settings.dev`, задано в `manage.py`).

Приложение будет доступно на http://127.0.0.1:8000/.

## Переключение окружений

- Разработка (по умолчанию): `DJANGO_SETTINGS_MODULE=helpdesk_project.settings.dev`
- Продакшен: `DJANGO_SETTINGS_MODULE=helpdesk_project.settings.prod`
  (требует заполненных `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`
  и, при переходе на PostgreSQL, `DATABASE_URL` в `.env`)

## Подключение PostgreSQL позже

1. `pip install psycopg2-binary` (раскомментировать в `requirements.txt`)
2. Добавить в `.env`:
   ```
   DATABASE_URL=postgres://user:password@host:5432/helpdesk_db
   ```
3. Настройка в `prod.py` уже готова читать `DATABASE_URL` автоматически —
   правки кода не требуются.

## Формы и crispy-forms

`django-crispy-forms` подключён с собственным (не Bootstrap) шаблон-паком
`custom` (`templates/custom/`), оформленным под простую вёрстку проекта
(`static/css/style.css`). Используется в `accounts` (вход, регистрация)
и `tickets` (создание заявки) через `{% load crispy_forms_tags %}` и
`{% crispy form %}`.
