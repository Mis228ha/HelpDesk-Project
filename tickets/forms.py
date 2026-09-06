from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from .models import Ticket


class TicketForm(forms.ModelForm):
    """Форма создания и редактирования заявки, оформленная через crispy-forms."""

    class Meta:
        model = Ticket
        fields = ["title", "description", "category", "status"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Сохранить заявку"))
