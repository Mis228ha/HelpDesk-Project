"""
Корневая конфигурация URL проекта helpdesk_project.
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("tickets/", include("tickets.urls")),
    path("", RedirectView.as_view(pattern_name="tickets:ticket_list", permanent=False)),
]