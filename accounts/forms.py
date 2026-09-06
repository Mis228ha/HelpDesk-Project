from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction

from .models import Profile


class RegisterForm(UserCreationForm):
    """
    Форма регистрации нового пользователя.

    После создания User автоматически создаёт связанный Profile
    с ролью «клиент» (Profile.Role.CLIENT).
    Рендерится в шаблоне через фильтр {{ form|crispy }}.
    """

    email = User._meta.get_field("email").formfield(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Profile.objects.create(user=user, role=Profile.Role.CLIENT)
        return user