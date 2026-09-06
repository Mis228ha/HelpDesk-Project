from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import RegisterForm


class RegisterView(CreateView):
    """
    Регистрация нового пользователя.

    RegisterForm сама создаёт связанный Profile (роль «клиент»);
    после успешной регистрации пользователь сразу авторизуется.
    """

    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("tickets:ticket_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class AccountLoginView(LoginView):
    """Вход пользователя (стандартная AuthenticationForm из django.contrib.auth)."""

    template_name = "accounts/login.html"


class AccountLogoutView(LogoutView):
    """Выход пользователя."""


class ProfileView(LoginRequiredMixin, TemplateView):
    """Простая страница профиля: только просмотр (username, email, роль)."""

    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = getattr(self.request.user, "profile", None)
        return context