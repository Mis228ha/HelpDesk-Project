import os
import re
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from accounts.models import Profile
from tickets.models import Attachment, Category, Comment, StatusHistory, Ticket

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
                "priority": Ticket.Priority.HIGH,
            },
        )

        new_ticket = Ticket.objects.get(title="Новая заявка")
        self.assertEqual(new_ticket.author, self.client1_user)
        self.assertEqual(new_ticket.status, Ticket.Status.NEW)
        self.assertEqual(new_ticket.priority, Ticket.Priority.HIGH)
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

    def test_status_change_creates_history_entry(self):
        self.client.login(username="admin", password="pass12345")
        self.assertEqual(self.ticket1.status, Ticket.Status.NEW)

        self.client.post(
            reverse("tickets:ticket_status_update", args=[self.ticket1.pk]),
            {"status": Ticket.Status.IN_PROGRESS},
        )

        entry = StatusHistory.objects.get(ticket=self.ticket1)
        self.assertEqual(entry.old_status, Ticket.Status.NEW)
        self.assertEqual(entry.new_status, Ticket.Status.IN_PROGRESS)
        self.assertEqual(entry.changed_by, self.admin_user)

    def test_submitting_same_status_does_not_create_history_entry(self):
        self.client.login(username="admin", password="pass12345")

        self.client.post(
            reverse("tickets:ticket_status_update", args=[self.ticket1.pk]),
            {"status": Ticket.Status.NEW},  # тот же статус, что уже стоит
        )

        self.assertFalse(StatusHistory.objects.filter(ticket=self.ticket1).exists())


class TicketDeleteViewTests(TicketViewTestBase):
    """TicketDeleteView: удаление только администратором и только через POST."""

    def delete_url(self, ticket):
        return reverse("tickets:ticket_delete", args=[ticket.pk])

    # --- права доступа ---------------------------------------------------

    def test_admin_can_delete_ticket(self):
        self.client.login(username="admin", password="pass12345")
        response = self.client.post(self.delete_url(self.ticket1), follow=True)

        # редирект на список и сообщение об успехе
        self.assertRedirects(response, reverse("tickets:ticket_list"))
        self.assertContains(response, "Заявка удалена")
        # заявка исчезла из БД, чужая осталась
        self.assertFalse(Ticket.objects.filter(pk=self.ticket1.pk).exists())
        self.assertTrue(Ticket.objects.filter(pk=self.ticket2.pk).exists())

    def test_client_cannot_delete_own_ticket(self):
        self.client.login(username="client1", password="pass12345")
        response = self.client.post(self.delete_url(self.ticket1))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Ticket.objects.filter(pk=self.ticket1.pk).exists())

    def test_client_cannot_delete_foreign_ticket(self):
        self.client.login(username="client1", password="pass12345")
        response = self.client.post(self.delete_url(self.ticket2))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Ticket.objects.filter(pk=self.ticket2.pk).exists())

    def test_anonymous_user_redirected_to_login(self):
        url = self.delete_url(self.ticket1)
        response = self.client.post(url)

        self.assertRedirects(response, f"{reverse('accounts:login')}?next={url}")
        self.assertTrue(Ticket.objects.filter(pk=self.ticket1.pk).exists())

    # --- только POST -------------------------------------------------------

    def test_get_request_returns_405_and_does_not_delete(self):
        self.client.login(username="admin", password="pass12345")
        response = self.client.get(self.delete_url(self.ticket1))

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Ticket.objects.filter(pk=self.ticket1.pk).exists())

    # --- каскадное удаление ----------------------------------------------

    def test_deleting_ticket_deletes_related_objects(self):
        Comment.objects.create(ticket=self.ticket1, author=self.client1_user, text="Вопрос")
        Comment.objects.create(ticket=self.ticket1, author=self.admin_user, text="Ответ")
        StatusHistory.objects.create(
            ticket=self.ticket1,
            old_status=Ticket.Status.NEW,
            new_status=Ticket.Status.IN_PROGRESS,
            changed_by=self.admin_user,
        )
        Attachment.objects.create(
            ticket=self.ticket1,
            file=SimpleUploadedFile("a.txt", b"data"),
            uploaded_by=self.client1_user,
        )
        # объекты другой заявки не должны пострадать
        Comment.objects.create(ticket=self.ticket2, author=self.client2_user, text="Чужой")

        self.client.login(username="admin", password="pass12345")
        with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            Attachment.objects.filter(ticket=self.ticket1).update(file="attachments/a.txt")
            self.client.post(self.delete_url(self.ticket1))

        self.assertEqual(Comment.objects.filter(ticket_id=self.ticket1.pk).count(), 0)
        self.assertEqual(StatusHistory.objects.filter(ticket_id=self.ticket1.pk).count(), 0)
        self.assertEqual(Attachment.objects.filter(ticket_id=self.ticket1.pk).count(), 0)
        self.assertEqual(Comment.objects.filter(ticket=self.ticket2).count(), 1)

    def test_deleting_ticket_removes_attachment_file_from_disk(self):
        with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            attachment = Attachment.objects.create(
                ticket=self.ticket1,
                file=SimpleUploadedFile("report.txt", b"content"),
                uploaded_by=self.client1_user,
            )
            file_path = attachment.file.path
            self.assertTrue(os.path.exists(file_path))

            self.client.login(username="admin", password="pass12345")
            # файл удаляется в on_commit — в TestCase такие колбэки выполняем явно
            with self.captureOnCommitCallbacks(execute=True):
                self.client.post(self.delete_url(self.ticket1))

            self.assertFalse(os.path.exists(file_path))

    # --- кнопка «Удалить» и модальное окно в HTML ------------------------

    def test_delete_button_visible_to_admin_on_detail_page(self):
        self.client.login(username="admin", password="pass12345")
        response = self.client.get(reverse("tickets:ticket_detail", args=[self.ticket1.pk]))

        self.assertContains(response, f'data-delete-url="{self.delete_url(self.ticket1)}"')
        self.assertContains(response, "Удалить</button>")
        self.assertContains(response, 'id="confirm-dialog"')

    def test_delete_buttons_visible_to_admin_in_list(self):
        self.client.login(username="admin", password="pass12345")
        response = self.client.get(reverse("tickets:ticket_list"))

        self.assertContains(response, f'data-delete-url="{self.delete_url(self.ticket1)}"')
        self.assertContains(response, f'data-delete-url="{self.delete_url(self.ticket2)}"')

    def test_delete_button_hidden_from_client(self):
        self.client.login(username="client1", password="pass12345")
        for url in (
            reverse("tickets:ticket_detail", args=[self.ticket1.pk]),
            reverse("tickets:ticket_list"),
        ):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, "data-delete-url")
            self.assertNotContains(response, "Удалить</button>")
            self.assertNotContains(response, 'id="confirm-dialog"')

    # --- CSRF ------------------------------------------------------------

    def test_dialog_form_carries_working_csrf_token(self):
        """Форма в <dialog> содержит csrf-токен, с которым удаление проходит."""
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.login(username="admin", password="pass12345")
        url = self.delete_url(self.ticket1)

        # без токена — 403, заявка на месте
        self.assertEqual(csrf_client.post(url).status_code, 403)
        self.assertTrue(Ticket.objects.filter(pk=self.ticket1.pk).exists())

        # токен берём из формы модального окна на странице заявки
        page = csrf_client.get(reverse("tickets:ticket_detail", args=[self.ticket1.pk]))
        dialog_html = page.content.decode().split('id="confirm-dialog"', 1)[1]
        token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', dialog_html).group(1)

        response = csrf_client.post(url, {"csrfmiddlewaretoken": token})
        self.assertRedirects(response, reverse("tickets:ticket_list"))
        self.assertFalse(Ticket.objects.filter(pk=self.ticket1.pk).exists())