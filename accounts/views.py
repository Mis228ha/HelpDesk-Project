from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import LoginForm, SignUpForm


class SignUpView(CreateView):
    """Регистрация нового пользователя с автоматическим входом."""

    form_class = SignUpForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("tickets:ticket_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class AccountLoginView(LoginView):
    """Вход пользователя."""

    authentication_form = LoginForm
    template_name = "accounts/login.html"


class AccountLogoutView(LogoutView):
    """Выход пользователя."""
    pass
