"""
Management-команда: python manage.py seed_db

Наполняет базу тестовыми данными для разработки/демо:
- 1 администратор (is_superuser=True, Profile.role="admin")
- 4 отдела (Department)
- 3 клиента (Profile.role="client"), распределённые по отделам
- 3 категории заявок
- 8-10 тестовых заявок в разных статусах, распределённых между клиентами
- комментарии к части заявок (от админа и авторов)

Идемпотентна: safe повторный запуск не создаёт дублей — пользователи/категории/
отделы ищутся через get_or_create, заявки и комментарии — через update_or_create
по естественному ключу (title / (ticket, author, text)). Пароли пользователей
переустанавливаются при каждом запуске на указанные ниже — так гарантируется,
что документированные логины/пароли всегда рабочие.

После выполнения в консоль выводится сводка созданных логинов/паролей/ролей.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Profile
from tickets.models import Category, Comment, Department, Ticket

User = get_user_model()

ADMIN = {
    "username": "admin",
    "password": "admin12345",
    "email": "admin@helpdesk.local",
    "department": "IT",
}

DEPARTMENT_NAMES = ["IT", "Бухгалтерия", "АХО", "Отдел кадров"]

CLIENTS = [
    {
        "username": "client1",
        "password": "client1pass123",
        "email": "client1@helpdesk.local",
        "department": "IT",
    },
    {
        "username": "client2",
        "password": "client2pass123",
        "email": "client2@helpdesk.local",
        "department": "Бухгалтерия",
    },
    {
        "username": "client3",
        "password": "client3pass123",
        "email": "client3@helpdesk.local",
        "department": "АХО",
    },
]

CATEGORY_NAMES = ["Оборудование", "Программное обеспечение", "Доступы"]

TICKETS = [
    {
        "title": "Не работает принтер на 3 этаже",
        "description": "Принтер HP LaserJet не печатает, горит красная лампочка.",
        "author": "client1",
        "category": "Оборудование",
        "priority": Ticket.Priority.LOW,
        "status": Ticket.Status.NEW,
    },
    {
        "title": "Завис компьютер в переговорке",
        "description": "Компьютер в переговорке №2 не реагирует на клавиатуру и мышь.",
        "author": "client1",
        "category": "Оборудование",
        "priority": Ticket.Priority.MEDIUM,
        "status": Ticket.Status.IN_PROGRESS,
    },
    {
        "title": "Не устанавливается 1С",
        "description": "При установке 1С:Бухгалтерия выдаёт ошибку лицензии.",
        "author": "client1",
        "category": "Программное обеспечение",
        "priority": Ticket.Priority.HIGH,
        "status": Ticket.Status.CLOSED,
    },
    {
        "title": "Нет доступа к общей папке",
        "description": "Не открывается сетевая папка \\\\fileserver\\finance, пишет «Доступ запрещён».",
        "author": "client2",
        "category": "Доступы",
        "priority": Ticket.Priority.CRITICAL,
        "status": Ticket.Status.NEW,
    },
    {
        "title": "Просьба выдать доступ к VPN",
        "description": "Нужен доступ к корпоративному VPN для удалённой работы.",
        "author": "client2",
        "category": "Доступы",
        "priority": Ticket.Priority.MEDIUM,
        "status": Ticket.Status.IN_PROGRESS,
    },
    {
        "title": "Тормозит браузер после обновления",
        "description": "После последнего обновления Chrome сильно тормозит и зависает.",
        "author": "client2",
        "category": "Программное обеспечение",
        "priority": Ticket.Priority.LOW,
        "status": Ticket.Status.CLOSED,
    },
    {
        "title": "Сломалась мышь",
        "description": "Беспроводная мышь перестала реагировать на движение.",
        "author": "client3",
        "category": "Оборудование",
        "priority": Ticket.Priority.MEDIUM,
        "status": Ticket.Status.NEW,
    },
    {
        "title": "Нужна лицензия на Photoshop",
        "description": "Для работы с макетами требуется лицензия Adobe Photoshop.",
        "author": "client3",
        "category": "Программное обеспечение",
        "priority": Ticket.Priority.LOW,
        "status": Ticket.Status.IN_PROGRESS,
    },
    {
        "title": "Забыл пароль от почты",
        "description": "Не могу войти в корпоративную почту, забыл пароль.",
        "author": "client3",
        "category": "Доступы",
        "priority": Ticket.Priority.CRITICAL,
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
    help = "Наполняет базу тестовыми данными: админ, клиенты, отделы, категории, заявки, комментарии."

    @transaction.atomic
    def handle(self, *args, **options):
        departments = {}
        for name in DEPARTMENT_NAMES:
            department, _ = Department.objects.get_or_create(name=name)
            departments[name] = department

        users = {}

        admin_user, admin_role, admin_dept_name = self._seed_user(
            ADMIN,
            role=Profile.Role.ADMIN,
            is_staff=True,
            is_superuser=True,
            department=departments[ADMIN["department"]],
        )
        users["admin"] = admin_user

        client_rows = []
        for client_data in CLIENTS:
            department = departments[client_data["department"]]
            user, role, dept_name = self._seed_user(
                client_data, role=Profile.Role.CLIENT, department=department
            )
            users[client_data["username"]] = user
            client_rows.append((client_data["username"], client_data["password"], role, dept_name))

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
                    "priority": t["priority"],
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
            f"  {ADMIN['username']:<10} / {ADMIN['password']:<16} — роль: {admin_role} (superuser), отдел: {admin_dept_name}"
        )
        for username, password, role, dept_name in client_rows:
            self.stdout.write(f"  {username:<10} / {password:<16} — роль: {role}, отдел: {dept_name}")

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Данные:"))
        self.stdout.write(f"  Отделы: {', '.join(DEPARTMENT_NAMES)}")
        self.stdout.write(f"  Категории: {', '.join(CATEGORY_NAMES)}")
        self.stdout.write(f"  Заявок создано/обновлено: {tickets_count}")
        self.stdout.write(f"  Комментариев создано/обновлено: {comments_count}")
        self.stdout.write("")

    @staticmethod
    def _seed_user(data, role, is_staff=False, is_superuser=False, department=None):
        """
        Создаёт (или обновляет пароль/флаги/отдел) пользователя и его Profile.
        Возвращает (user, role_display, department_name_or_dash).
        """
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

        profile, _ = Profile.objects.get_or_create(
            user=user, defaults={"role": role, "department": department}
        )
        changed = False
        if profile.role != role:
            profile.role = role
            changed = True
        if profile.department_id != (department.id if department else None):
            profile.department = department
            changed = True
        if changed:
            profile.save()

        return user, profile.get_role_display(), (department.name if department else "—")