from django.conf import settings
from django.db import models
from django.urls import reverse


class Ticket(models.Model):
    """Заявка в службу поддержки."""

    class Status(models.TextChoices):
        OPEN = "open", "Открыта"
        IN_PROGRESS = "in_progress", "В работе"
        CLOSED = "closed", "Закрыта"

    class Priority(models.TextChoices):
        LOW = "low", "Низкий"
        MEDIUM = "medium", "Средний"
        HIGH = "high", "Высокий"

    title = models.CharField("Заголовок", max_length=200)
    description = models.TextField("Описание")
    status = models.CharField(
        "Статус", max_length=20, choices=Status.choices, default=Status.OPEN
    )
    priority = models.CharField(
        "Приоритет", max_length=20, choices=Priority.choices, default=Priority.MEDIUM
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    created_at = models.DateTimeField("Создана", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлена", auto_now=True)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("tickets:ticket_detail", kwargs={"pk": self.pk})
