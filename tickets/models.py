import os

from django.conf import settings
from django.db import models
from django.urls import reverse


class Department(models.Model):
    """Отдел организации (используется в профиле пользователя, accounts.Profile)."""

    name = models.CharField("Название", max_length=100)

    class Meta:
        verbose_name = "Отдел"
        verbose_name_plural = "Отделы"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Category(models.Model):
    """Категория заявки (например: «Оборудование», «ПО», «Доступы»)."""

    name = models.CharField("Название", max_length=100)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Ticket(models.Model):
    """Заявка в службу поддержки."""

    class Status(models.TextChoices):
        NEW = "new", "Новая"
        IN_PROGRESS = "in_progress", "В работе"
        CLOSED = "closed", "Закрыта"

    class Priority(models.TextChoices):
        LOW = "low", "Низкий"
        MEDIUM = "medium", "Средний"
        HIGH = "high", "Высокий"
        CRITICAL = "critical", "Критический"

    title = models.CharField("Заголовок", max_length=200)
    description = models.TextField("Описание")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        on_delete=models.PROTECT,
        related_name="tickets",
    )
    priority = models.CharField(
        "Приоритет", max_length=20, choices=Priority.choices, default=Priority.MEDIUM
    )
    status = models.CharField(
        "Статус", max_length=20, choices=Status.choices, default=Status.NEW
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


class Comment(models.Model):
    """Комментарий к заявке (переписка автора и поддержки)."""

    ticket = models.ForeignKey(
        Ticket,
        verbose_name="Заявка",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    text = models.TextField("Текст")
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Комментарий {self.author} к «{self.ticket}»"


class StatusHistory(models.Model):
    """
    История изменений статуса заявки (аудит-лог).

    changed_by использует on_delete=SET_NULL, чтобы при удалении
    пользователя запись истории не пропадала — это журнал, его нельзя
    терять даже если автор изменения позже удалён из системы.
    """

    ticket = models.ForeignKey(
        Ticket,
        verbose_name="Заявка",
        on_delete=models.CASCADE,
        related_name="status_history",
    )
    old_status = models.CharField(
        "Старый статус", max_length=20, choices=Ticket.Status.choices
    )
    new_status = models.CharField(
        "Новый статус", max_length=20, choices=Ticket.Status.choices
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Кто изменил",
        on_delete=models.SET_NULL,
        null=True,
        related_name="status_changes",
    )
    changed_at = models.DateTimeField("Когда изменено", auto_now_add=True)

    class Meta:
        verbose_name = "История статуса"
        verbose_name_plural = "История статусов"
        ordering = ["-changed_at"]

    def __str__(self):
        return f"{self.ticket}: {self.old_status} → {self.new_status}"


class Attachment(models.Model):
    """Файл, прикреплённый к заявке (создаётся вместе с заявкой или отдельно)."""

    ticket = models.ForeignKey(
        Ticket,
        verbose_name="Заявка",
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    file = models.FileField("Файл", upload_to="attachments/%Y/%m/")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Загрузил",
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    uploaded_at = models.DateTimeField("Загружен", auto_now_add=True)

    class Meta:
        verbose_name = "Вложение"
        verbose_name_plural = "Вложения"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.filename

    @property
    def filename(self):
        """Имя файла без пути (attachments/2026/09/x.pdf -> x.pdf) — для отображения в шаблонах."""
        return os.path.basename(self.file.name)