from django import forms

from .models import Comment, Ticket


class TicketForm(forms.ModelForm):
    """
    Форма создания заявки: title, description, category.

    author проставляется во view (request.user), status не входит в форму
    и остаётся равным значению по умолчанию модели ("new").
    Рендерится в шаблоне через фильтр {{ form|crispy }}.
    """

    class Meta:
        model = Ticket
        fields = ["title", "description", "category"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
        }


class CommentForm(forms.ModelForm):
    """Форма добавления комментария к заявке. ticket и author проставляются во view."""

    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 3, "placeholder": "Напишите комментарий..."}),
        }
        labels = {
            "text": "Комментарий",
        }


class TicketStatusForm(forms.ModelForm):
    """Форма смены статуса заявки — доступна только администратору (см. TicketStatusUpdateView)."""

    class Meta:
        model = Ticket
        fields = ["status"]