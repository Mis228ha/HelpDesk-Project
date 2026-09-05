from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView, ListView

from .forms import TicketForm
from .models import Ticket


class TicketListView(LoginRequiredMixin, ListView):
    """Список заявок текущего пользователя."""

    model = Ticket
    template_name = "tickets/ticket_list.html"
    context_object_name = "tickets"
    paginate_by = 10

    def get_queryset(self):
        return Ticket.objects.filter(author=self.request.user)


class TicketDetailView(LoginRequiredMixin, DetailView):
    """Детальная карточка одной заявки."""

    model = Ticket
    template_name = "tickets/ticket_detail.html"
    context_object_name = "ticket"

    def get_queryset(self):
        return Ticket.objects.filter(author=self.request.user)


class TicketCreateView(LoginRequiredMixin, CreateView):
    """Создание новой заявки."""

    model = Ticket
    form_class = TicketForm
    template_name = "tickets/ticket_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
