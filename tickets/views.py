from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from accounts.mixins import AdminRequiredMixin
from accounts.models import Profile

from .forms import CommentForm, TicketForm, TicketStatusForm
from .models import Comment, Ticket


def _is_admin(user):
    """Хелпер: True, если у пользователя есть Profile с ролью admin."""
    profile = getattr(user, "profile", None)
    return profile is not None and profile.role == Profile.Role.ADMIN


class TicketListView(LoginRequiredMixin, ListView):
    """
    Список заявок в виде карточек.
    - клиент (role == "client") видит только свои заявки;
    - админ (role == "admin") видит все заявки.
    """

    model = Ticket
    template_name = "tickets/ticket_list.html"
    context_object_name = "tickets"
    paginate_by = 12

    def get_queryset(self):
        qs = Ticket.objects.select_related("author", "category")
        if _is_admin(self.request.user):
            return qs
        return qs.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = _is_admin(self.request.user)
        return context


class TicketCreateView(LoginRequiredMixin, CreateView):
    """
    Создание заявки: доступно любому авторизованному пользователю.
    author = request.user, status по умолчанию остаётся "new" (не входит в форму).
    """

    model = Ticket
    form_class = TicketForm
    template_name = "tickets/ticket_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class TicketDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Детальная карточка заявки: сама заявка, список комментариев,
    форма добавления комментария.

    Доступ: автор заявки (клиент) или пользователь с ролью admin.
    """

    model = Ticket
    template_name = "tickets/ticket_detail.html"
    context_object_name = "ticket"

    def get_object(self, queryset=None):
        # Кэшируем объект, чтобы test_func() и get() не делали два одинаковых запроса.
        if not hasattr(self, "_ticket_object"):
            self._ticket_object = super().get_object(queryset)
        return self._ticket_object

    def test_func(self):
        ticket = self.get_object()
        if _is_admin(self.request.user):
            return True
        return ticket.author_id == self.request.user.id

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = self.object.comments.select_related("author")
        context["comment_form"] = CommentForm()
        context["is_admin"] = _is_admin(self.request.user)
        return context


class CommentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Добавление комментария к заявке.
    Доступ: автор заявки (клиент, только к своей заявке) или админ (к любой).
    При ошибке валидации заново показывает страницу заявки с ошибками формы.
    """

    model = Comment
    form_class = CommentForm
    template_name = "tickets/ticket_detail.html"

    def get_ticket(self):
        if not hasattr(self, "_ticket"):
            self._ticket = get_object_or_404(Ticket, pk=self.kwargs["pk"])
        return self._ticket

    def test_func(self):
        ticket = self.get_ticket()
        if _is_admin(self.request.user):
            return True
        return ticket.author_id == self.request.user.id

    def form_valid(self, form):
        form.instance.ticket = self.get_ticket()
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("tickets:ticket_detail", kwargs={"pk": self.kwargs["pk"]})

    def get_context_data(self, **kwargs):
        # Используется только при form_invalid — заново рендерим ticket_detail.html.
        context = super().get_context_data(**kwargs)
        ticket = self.get_ticket()
        context["ticket"] = ticket
        context["comments"] = ticket.comments.select_related("author")
        context["comment_form"] = kwargs.get("form") or CommentForm()
        context["is_admin"] = _is_admin(self.request.user)
        return context


class TicketStatusUpdateView(AdminRequiredMixin, UpdateView):
    """
    Смена статуса заявки — доступна только администратору.
    Простая форма с select из new/in_progress/closed.
    """

    model = Ticket
    form_class = TicketStatusForm
    template_name = "tickets/ticket_status_form.html"
    context_object_name = "ticket"

    def get_success_url(self):
        return reverse("tickets:ticket_detail", kwargs={"pk": self.object.pk})