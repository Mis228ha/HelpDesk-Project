from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import Profile


def admin_required(view_func):
    """
    Декоратор для функциональных view (аналог AdminRequiredMixin для CBV):
    пропускает только пользователей с Profile.role == Profile.Role.ADMIN.

    - анонимный пользователь -> редирект на страницу входа (через login_required);
    - авторизован, но не admin -> 403 Forbidden (PermissionDenied).

    Использование:
        @admin_required
        def some_admin_view(request):
            ...
    """

    @login_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        profile = getattr(request.user, "profile", None)
        if profile is None or profile.role != Profile.Role.ADMIN:
            raise PermissionDenied("Доступ разрешён только администраторам.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view