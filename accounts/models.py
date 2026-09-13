from django.conf import settings
from django.db import models

from tickets.models import Department


class Profile(models.Model):
    """Дополнительный профиль пользователя с ролью в системе поддержки."""

    class Role(models.TextChoices):
        CLIENT = "client", "Клиент"
        ADMIN = "admin", "Администратор"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(
        "Роль", max_length=20, choices=Role.choices, default=Role.CLIENT
    )
    department = models.ForeignKey(
        Department,
        verbose_name="Отдел",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profiles",
    )

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"