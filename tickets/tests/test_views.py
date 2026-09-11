from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile
from tickets.models import Category, Ticket

User = get_user_model()


class TicketViewTestBase(TestCase):
    """
    Общий сетап для тестов views: категория, два клиента (каждый со своей
    заявкой) и один админ. Конкретные TestCase-классы наследуются от этого.
    """

    def setUp(self):
        self.category = Category.objects.create(name="Оборудование")

        self.client1_user = User.objects.create_user(username="client1", password="pass12345")
        Profile.objects.create(user=self.client1_user, role=Profile.Role.CLIENT)

        self.client2_user = User.objects.create_user(username="client2", password="pass12345")
        Profile.objects.create(user=self.client2_user, role=Profile.Role.CLIENT)

        self.admin_user = User.objects.create_user(username="admin", password="pass12345")
        Profile.objects.create(user=self.admin_user, role=Profile.Role.ADMIN)

        self.ticket1 = Ticket.objects.create(
            title="Заявка клиента 1",
            description="Описание заявки клиента 1",
            author=self.client1_user,
            category=self.category,
        )
        self.ticket2 = Ticket.objects.create(
            title="Заявка клиента 2",
            description="Описание заявки клиента 2",
            author=self.client2_user,
            category=self.category,
        )


class TicketCreateViewTests(TicketViewTestBase):
    """TicketCreateView: доступность и корректность создания заявки."""

    def test_authenticated_client_can_create_ticket(self):
        self.client.login(username="client1", password="pass12345")
        response = self.client.post(
            reverse("tickets:ticket_create"),
            {
                "title": "Новая заявка",
                "description": "Описание новой заявки",
                "category": self.category.pk,
            },
        )

        new_ticket = Ticket.objects.get(title="Новая заявка")
        self.assertEqual(new_ticket.author, self.client1_user)
        self.assertEqual(new_ticket.status, Ticket.Status.NEW)
        self.assertRedirects(response, new_ticket.get_absolute_url())

    def test_anonymous_user_redirected_to_login(self):
        create_url = reverse("tickets:ticket_create")
        response = self.client.get(create_url)

        expected_url = f"{reverse('accounts:login')}?next={create_url}"
        self.assertRedirects(response, expected_url)
        # Убедимся, что ничего не создалось.
        self.assertEqual(Ticket.objects.count(), 2)


class TicketListViewTests(TicketViewTestBase):
    """TicketListView: клиент видит только свои заявки, админ — все."""

    def test_client_sees_only_own_tickets(self):
        self.client.login(username="client1", password="pass12345")
        response = self.client.get(reverse("tickets:ticket_list"))

        tickets_in_context = list(response.context["tickets"])
        self.assertIn(self.ticket1, tickets_in_context)
        self.assertNotIn(self.ticket2, tickets_in_context)

    def test_admin_sees_all_tickets(self):
        self.client.login(username="admin", password="pass12345")
        response = self.client.get(reverse("tickets:ticket_list"))

        tickets_in_context = list(response.context["tickets"])
        self.assertIn(self.ticket1, tickets_in_context)
        self.assertIn(self.ticket2, tickets_in_context)


class TicketStatusUpdateViewTests(TicketViewTestBase):
    """TicketStatusUpdateView: доступ только у админа (AdminRequiredMixin)."""

    def test_client_cannot_open_status_update_for_own_ticket(self):
        self.client.login(username="client1", password="pass12345")
        response = self.client.get(
            reverse("tickets:ticket_status_update", args=[self.ticket1.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_client_cannot_open_status_update_for_foreign_ticket(self):
        self.client.login(username="client1", password="pass12345")
        response = self.client.get(
            reverse("tickets:ticket_status_update", args=[self.ticket2.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_redirected_to_login(self):
        status_url = reverse("tickets:ticket_status_update", args=[self.ticket1.pk])
        response = self.client.get(status_url)

        expected_url = f"{reverse('accounts:login')}?next={status_url}"
        self.assertRedirects(response, expected_url)

    def test_admin_can_change_status(self):
        self.client.login(username="admin", password="pass12345")
        response = self.client.post(
            reverse("tickets:ticket_status_update", args=[self.ticket1.pk]),
            {"status": Ticket.Status.IN_PROGRESS},
        )

        self.ticket1.refresh_from_db()
        self.assertEqual(self.ticket1.status, Ticket.Status.IN_PROGRESS)
        self.assertRedirects(
            response, reverse("tickets:ticket_detail", args=[self.ticket1.pk])
        )