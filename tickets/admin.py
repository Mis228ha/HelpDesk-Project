from django.contrib import admin

from .models import Category, Comment, Department, StatusHistory, Ticket


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "category", "status", "created_at", "updated_at")
    list_filter = ("status", "category")
    search_fields = ("title", "description")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "ticket", "author", "created_at")
    list_filter = ("created_at",)
    search_fields = ("text",)


@admin.register(StatusHistory)
class StatusHistoryAdmin(admin.ModelAdmin):
    """Только для чтения: история статусов — это аудит-лог, руками её не редактируют."""

    list_display = ("id", "ticket", "old_status", "new_status", "changed_by", "changed_at")
    list_filter = ("old_status", "new_status")
    search_fields = ("ticket__title",)
    readonly_fields = [f.name for f in StatusHistory._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False