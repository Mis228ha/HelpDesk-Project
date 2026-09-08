"""
Management-команда: python manage.py seed_db

Наполняет базу тестовыми данными для разработки/демо:
- 1 администратор (is_superuser=True, Profile.role="admin")
- 3 клиента (Profile.role="client")
- 3 категории заявок
- 8-10 тестовых заявок в разных статусах, распределённых между клиентами
- комментарии к части заявок (от админа и авторов)

Идемпотентна: safe повторный запуск не создаёт дублей — пользователи/категории
ищутся через get_or_create, заявки и комментарии — через update_or_create
по естественному ключу (title / (ticket, author, text)). Пароли пользователей
переустанавливаются при каждом запуске на указанные ниже — так гарантируется,
что документированные логины/пароли всегда рабочие.

После выполнения в консоль выводится сводка созданных логинов/паролей/ролей.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Profile
from tickets.models import Category, Comment, Ticket

User = get_user_model()

ADMIN = {"username": "admin", "password": "admin12345", "email": "admin@helpdesk.local"}

CLIENTS = [
    {"username": "client1", "password": "client1pass123", "email": "client1@helpdesk.local"},
    {"username": "client2", "password": "client2pass123", "email": "client2@helpdesk.local"},
    {"username": "client3", "password": "client3pass123", "email": "client3@helpdesk.local"},
]

CATEGORY_NAMES = ["Оборудование", "Программное обеспечение", "Доступы"]

TICKETS = [
    {
        "title": "Не работает принтер на 3 этаже",
        "description": "Принтер HP LaserJet не печатает, горит красная лампочка.",
        "author": "client1",
        "category": "Оборудование",
        "status": Ticket.Status.NEW,
    },
    {
        "title": "Завис компьютер в переговорке",
        "description": "Компьютер в переговорке №2 не реагирует на клавиатуру и мышь.",
        "author": "client1",
        "category": "Оборудование",
        "status": Ticket.Status.IN_PROGRESS,
    },
    {
        "title": "Не устанавливается 1С",
        "description": "При установке 1С:Бухгалтерия выдаёт ошибку лицензии.",
        "author": "client1",
        "category": "Программное обеспечение",
        "status": Ticket.Status.CLOSED,
    },
    {
        "title": "Нет доступа к общей папке",
        "description": "Не открывается сетевая папка \\\\fileserver\\finance, пишет «Доступ запрещён».",
        "author": "client2",
        "category": "Доступы",
        "status": Ticket.Status.NEW,
    },
    {
        "title": "Просьба выдать доступ к VPN",
        "description": "Нужен доступ к корпоративному VPN для удалённой работы.",
        "author": "client2",
        "category": "Доступы",
        "status": Ticket.Status.IN_PROGRESS,
    },
    {
        "title": "Тормозит браузер после обновления",
        "description": "После последнего обновления Chrome сильно тормозит и зависает.",
        "author": "client2",
        "category": "Программное обеспечение",
        "status": Ticket.Status.CLOSED,
    },
    {
        "title": "Сломалась мышь",
        "description": "Беспроводная мышь перестала реагировать на движение.",
        "author": "client3",
        "category": "Оборудование",
        "status": Ticket.Status.NEW,
    },
    {
        "title": "Нужна лицензия на Photoshop",
        "description": "Для работы с макетами требуется лицензия Adobe Photoshop.",
        "author": "client3",
        "category": "Программное обеспечение",
        "status": Ticket.Status.IN_PROGRESS,
    },
    {
        "title": "Забыл пароль от почты",
        "description": "Не могу войти в корпоративную почту, забыл пароль.",
        "author": "client3",
        "category": "Доступы",
        "status": Ticket.Status.CLOSED,
    },
]

COMMENTS = [
    {
        "ticket": "Не работает принтер на 3 этаже",
        "author": "admin",
        "text": "Приняли заявку в работу, отправили техника.",
    },
    {
        "ticket": "Завис компьютер в переговорке",
        "author": "admin",
        "text": "Проверяем, похоже требуется переустановка драйверов.",
    },
    {
        "ticket": "Завис компьютер в переговорке",
        "author": "client1",
        "text": "Спасибо, жду обновлений по заявке.",
    },
    {
        "ticket": "Не устанавливается 1С",
        "author": "admin",
        "text": "Проблема решена, установка выполнена удалённо.",
    },
    {
        "ticket": "Нет доступа к общей папке",
        "author": "admin",
        "text": "Уточните, пожалуйста, точное название папки и ваш логин.",
    },
    {
        "ticket": "Тормозит браузер после обновления",
        "author": "admin",
        "text": "Переустановили расширения браузера, попробуйте сейчас.",
    },
    {
        "ticket": "Тормозит браузер после обновления",
        "author": "client2",
        "text": "Да, теперь всё работает быстро, спасибо!",
    },
    {
        "ticket": "Забыл пароль от почты",
        "author": "admin",
        "text": "Пароль сброшен, новый выслан на резервный адрес.",
    },
]


class Command(BaseCommand):
    help = "Наполняет базу тестовыми данными: админ, клиенты, категории, заявки, комментарии."

    @transaction.atomic
    def handle(self, *args, **options):
        users = {}

        admin_user, admin_role = self._seed_user(
            ADMIN, role=Profile.Role.ADMIN, is_staff=True, is_superuser=True
        )
        users["admin"] = admin_user

        client_rows = []
        for client_data in CLIENTS:
            user, role = self._seed_user(client_data, role=Profile.Role.CLIENT)
            users[client_data["username"]] = user
            client_rows.append((client_data["username"], client_data["password"], role))

        categories = {}
        for name in CATEGORY_NAMES:
            category, _ = Category.objects.get_or_create(name=name)
            categories[name] = category

        tickets_count = 0
        tickets_by_title = {}
        for t in TICKETS:
            ticket, _ = Ticket.objects.update_or_create(
                title=t["title"],
                defaults={
                    "description": t["description"],
                    "author": users[t["author"]],
                    "category": categories[t["category"]],
                    "status": t["status"],
                },
            )
            tickets_by_title[t["title"]] = ticket
            tickets_count += 1

        comments_count = 0
        for c in COMMENTS:
            Comment.objects.update_or_create(
                ticket=tickets_by_title[c["ticket"]],
                author=users[c["author"]],
                text=c["text"],
            )
            comments_count += 1

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("База успешно наполнена тестовыми данными."))
        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Созданные аккаунты:"))
        self.stdout.write(
            f"  {ADMIN['username']:<10} / {ADMIN['password']:<16} — роль: {admin_role} (superuser)"
        )
        for username, password, role in client_rows:
            self.stdout.write(f"  {username:<10} / {password:<16} — роль: {role}")

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Данные:"))
        self.stdout.write(f"  Категории: {', '.join(CATEGORY_NAMES)}")
        self.stdout.write(f"  Заявок создано/обновлено: {tickets_count}")
        self.stdout.write(f"  Комментариев создано/обновлено: {comments_count}")
        self.stdout.write("")

    @staticmethod
    def _seed_user(data, role, is_staff=False, is_superuser=False):
        """Создаёт (или обновляет пароль/флаги) пользователя и его Profile. Возвращает (user, role_display)."""
        user, created = User.objects.get_or_create(
            username=data["username"],
            defaults={"email": data["email"]},
        )
        user.email = data["email"]
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.is_active = True
        user.set_password(data["password"])
        user.save()

        profile, _ = Profile.objects.get_or_create(user=user, defaults={"role": role})
        if profile.role != role:
            profile.role = role
            profile.save()

        return user, profile.get_role_display()