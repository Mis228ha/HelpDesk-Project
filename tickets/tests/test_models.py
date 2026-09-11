from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from accounts.models import Profile
from tickets.forms import TicketForm
from tickets.models import Category, Ticket

User = get_user_model()


class TicketModelTests(TestCase):
    """Базовое поведение модели Ticket."""

    def setUp(self):
        self.category = Category.objects.create(name="Оборудование")
        self.author = User.objects.create_user(username="client1", password="pass12345")
        Profile.objects.create(user=self.author, role=Profile.Role.CLIENT)

    def test_default_status_is_new(self):
        """При создании без явного статуса заявка получает статус 'new'."""
        ticket = Ticket.objects.create(
            title="Не работает мышь",
            description="Описание проблемы",
            author=self.author,
            category=self.category,
        )
        self.assertEqual(ticket.status, Ticket.Status.NEW)

    def test_str_returns_title(self):
        ticket = Ticket.objects.create(
            title="Заголовок заявки",
            description="Описание проблемы",
            author=self.author,
            category=self.category,
        )
        self.assertEqual(str(ticket), "Заголовок заявки")

    def test_tickets_are_ordered_newest_first(self):
        """Meta.ordering = ['-created_at'] — свежие заявки должны идти первыми."""
        first = Ticket.objects.create(
            title="Первая заявка",
            description="Описание",
            author=self.author,
            category=self.category,
        )
        # Искусственно "состариваем" первую заявку, чтобы тест не зависел
        # от точности системных часов между двумя create() подряд.
        Ticket.objects.filter(pk=first.pk).update(
            created_at=timezone.now() - timedelta(minutes=5)
        )
        second = Ticket.objects.create(
            title="Вторая заявка",
            description="Описание",
            author=self.author,
            category=self.category,
        )

        titles = list(Ticket.objects.values_list("title", flat=True))
        self.assertEqual(titles, ["Вторая заявка", "Первая заявка"])


class TicketFormValidationTests(TestCase):
    """TicketForm: обязательность полей title/description."""

    def setUp(self):
        self.category = Category.objects.create(name="Оборудование")

    def test_title_is_required(self):
        form = TicketForm(
            data={"title": "", "description": "Описание проблемы", "category": self.category.pk}
        )
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_description_is_required(self):
        form = TicketForm(
            data={"title": "Заголовок заявки", "description": "", "category": self.category.pk}
        )
        self.assertFalse(form.is_valid())
        self.assertIn("description", form.errors)

    def test_valid_data_passes_validation(self):
        form = TicketForm(
            data={
                "title": "Заголовок заявки",
                "description": "Описание проблемы",
                "category": self.category.pk,
            }
        )
        self.assertTrue(form.is_valid())