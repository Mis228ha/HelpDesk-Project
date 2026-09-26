from django import forms

from .models import Attachment, Comment, Ticket


class TicketForm(forms.ModelForm):
    """
    Форма создания заявки: title, description, category, priority
    + необязательное вложение (file, не поле модели Ticket).

    author проставляется во view (request.user), status не входит в форму
    и остаётся равным значению по умолчанию модели ("new"). Если файл
    передан, TicketCreateView создаст для него отдельный Attachment.
    Рендерится в шаблоне через фильтр {{ form|crispy }}.
    """

    file = forms.FileField(required=False, label="Вложение (необязательно)")

    class Meta:
        model = Ticket
        fields = ["title", "description", "category", "priority"]
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


class AttachmentForm(forms.ModelForm):
    """
    Форма добавления вложения к уже существующей заявке.
    ticket и uploaded_by проставляются во view.
    """

    class Meta:
        model = Attachment
        fields = ["file"]
        labels = {
            "file": "Файл",
        }