from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction

from tickets.models import Department

from .models import Profile


class RegisterForm(UserCreationForm):
    """
    Форма регистрации нового пользователя.

    Помимо стандартных полей UserCreationForm добавляет выбор отдела
    (Department). После создания User автоматически создаёт связанный
    Profile с ролью «клиент» (Profile.Role.CLIENT) и выбранным отделом.
    Рендерится в шаблоне через фильтр {{ form|crispy }}.
    """

    email = User._meta.get_field("email").formfield(required=True)
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=True,
        label="Отдел",
        empty_label="Выберите отдел",
    )

    # Порядок полей при рендере через {{ form|crispy }}: без этого department
    # оказался бы в самом конце (после password1/password2), т.к. это поле
    # не входит в Meta.fields и по умолчанию добавляется последним.
    field_order = ["username", "email", "department", "password1", "password2"]

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Profile.objects.create(
                user=user,
                role=Profile.Role.CLIENT,
                department=self.cleaned_data["department"],
            )
        return user