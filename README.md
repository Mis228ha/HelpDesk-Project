# Helpdesk Project (MVP)

Учебный MVP-проект службы поддержки на Django. Пользователи с ролью
«клиент» создают заявки и переписываются по ним в комментариях; пользователи
с ролью «администратор» видят все заявки и управляют их статусом.

## Стек

- **Python 3.10**
- **Django 4.2** (LTS)
- **SQLite** — база данных для разработки (PostgreSQL подключается позже через `DATABASE_URL`, см. `helpdesk_project/settings/prod.py`)
- **django-crispy-forms** — рендеринг форм через собственный шаблон-пак `custom` (`templates/custom/`), без Bootstrap
- **vanilla HTML/CSS** — вёрстка без CSS-фреймворков и без JavaScript
- **django-environ** — настройки через `.env`

## Роли и функционал

В MVP два типа пользователей, роль хранится в `accounts.Profile.role`.

### Клиент (`role = client`)

- регистрация, вход, выход;
- просмотр своего профиля (логин, email, роль);
- создание заявки (заголовок, описание, категория; статус всегда выставляется `new` автоматически);
- список **только своих** заявок, карточками (заголовок, статус, дата, категория);
- детальная страница своей заявки с историей комментариев;
- добавление комментариев к своей заявке.

### Администратор (`role = admin`)

Всё то же, что и клиент, плюс:

- список **всех** заявок всех клиентов;
- просмотр любой заявки и комментариев к ней;
- добавление комментариев к любой заявке;
- смена статуса любой заявки (`new` / `in_progress` / `closed`);
- полный доступ к Django admin (`/admin/`) — управление пользователями, категориями, заявками и комментариями напрямую.

Разграничение доступа реализовано через `UserPassesTestMixin`:
`accounts/mixins.py` (`AdminRequiredMixin` для CBV) и `accounts/decorators.py`
(`admin_required` — аналог для функциональных views). Для заявок клиент
всегда сверяется с `ticket.author`, администратор проходит проверку по
`profile.role == "admin"`.

## Установка и запуск

Требуется Python 3.10.

```bash
git clone <URL-репозитория>
cd helpdesk_project

python3.10 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # для разработки можно не редактировать

python manage.py migrate
python manage.py seed_db        # наполняет базу тестовыми данными (см. ниже)
python manage.py runserver
```

Приложение будет доступно на **http://127.0.0.1:8000/** (редиректит на
`/tickets/`). По умолчанию используются настройки разработки
(`helpdesk_project.settings.dev` — SQLite, DEBUG=True).

Вместо `seed_db` данные можно загрузить готовой фикстурой:

```bash
python manage.py loaddata fixtures/initial_data.json
```

Обе команды дают один и тот же набор данных — см. таблицу ниже.

## Тестовые учётные записи

Создаются командой `seed_db` (или `loaddata fixtures/initial_data.json`):

| Логин     | Пароль            | Роль                  |
|-----------|-------------------|------------------------|
| `admin`   | `admin12345`      | Администратор (superuser) |
| `client1` | `client1pass123`  | Клиент                |
| `client2` | `client2pass123`  | Клиент                |
| `client3` | `client3pass123`  | Клиент                |

Также создаются 3 категории («Оборудование», «Программное обеспечение»,
«Доступы») и 8–10 тестовых заявок в разных статусах, часть — с комментариями.

## Тесты

```bash
python manage.py test
```

Покрыто (`tickets/tests/`): модель `Ticket` (дефолтный статус, `__str__`,
сортировка), обязательность полей `title`/`description` в `TicketForm`,
создание заявки авторизованным клиентом, редирект анонима на страницу входа,
фильтрация списка заявок по роли (клиент видит только свои, админ — все),
доступ к смене статуса только у администратора.

## Структура проекта

```
helpdesk_project/
├── manage.py
├── requirements.txt
├── .env.example
├── fixtures/
│   └── initial_data.json          # альтернатива seed_db через loaddata
│
├── helpdesk_project/               # пакет настроек и корневой urls.py
│   ├── settings/
│   │   ├── base.py                 # общие настройки
│   │   ├── dev.py                  # разработка (SQLite, DEBUG=True)
│   │   └── prod.py                 # продакшен (заготовка под PostgreSQL)
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                       # пользователи, роли, доступ
│   ├── models.py                   # Profile (user, role: client/admin)
│   ├── forms.py                    # RegisterForm
│   ├── views.py                    # Register/Login/Logout/Profile
│   ├── mixins.py                   # AdminRequiredMixin
│   └── decorators.py               # admin_required
│
├── tickets/                        # заявки, категории, комментарии
│   ├── models.py                   # Category, Ticket, Comment
│   ├── forms.py                    # TicketForm, CommentForm, TicketStatusForm
│   ├── views.py                    # List/Create/Detail/Comment/StatusUpdate
│   ├── management/commands/
│   │   └── seed_db.py              # наполнение базы тестовыми данными
│   └── tests/
│       ├── test_models.py
│       └── test_views.py
│
├── templates/
│   ├── base.html                   # header / nav / content / footer
│   ├── accounts/                   # login.html, register.html, profile.html
│   ├── tickets/                    # ticket_list/detail/form/status_form.html
│   └── custom/                     # шаблон-пак django-crispy-forms
│
└── static/css/style.css            # вся вёрстка проекта
```

## Основные URL

| URL | Описание |
|---|---|
| `/tickets/` | список заявок (свои — клиенту, все — админу) |
| `/tickets/create/` | создание заявки |
| `/tickets/<pk>/` | детальная страница заявки + комментарии |
| `/tickets/<pk>/status/` | смена статуса (только админ) |
| `/tickets/<pk>/comment/` | добавление комментария |
| `/accounts/register/` | регистрация |
| `/accounts/login/` | вход |
| `/accounts/logout/` | выход |
| `/accounts/profile/` | профиль (просмотр) |
| `/admin/` | Django admin |

## Что не реализовано в MVP / планируется дальше

- **Department** — отделы/подразделения, привязка заявок и сотрудников к отделу.
- **Attachment** — прикрепление файлов к заявкам и комментариям.
- **StatusHistory** — история изменений статуса заявки (кто, когда, с какого на какой статус переключил).
- **Приоритеты заявок** (low/medium/high) и, возможно, SLA по приоритету.
- **Фильтрация и поиск** по списку заявок — по статусу, категории, дате, автору.
- **Уведомления** — email или in-app уведомления о новых заявках/комментариях/смене статуса.
- **Статистика и дашборды** для администратора — количество заявок по статусам/категориям, среднее время закрытия и т.п.