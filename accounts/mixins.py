from django.contrib.auth.mixins import UserPassesTestMixin

from .models import Profile


class AdminRequiredMixin(UserPassesTestMixin):
    """
    Class-Based View mixin: пропускает только пользователей, у которых
    есть Profile с role == Profile.Role.ADMIN.

    Поведение (стандартное для UserPassesTestMixin):
    - анонимный пользователь -> редирект на LOGIN_URL;
    - авторизован, но роль не admin (или профиля нет) -> 403 Forbidden.

    Использование:
        class SomeAdminView(AdminRequiredMixin, ListView):
            ...
    """

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        profile = getattr(user, "profile", None)
        return profile is not None and profile.role == Profile.Role.ADMIN