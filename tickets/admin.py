from django.contrib import admin

from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "priority", "created_at")
    list_filter = ("status", "priority")
    search_fields = ("title", "description")
