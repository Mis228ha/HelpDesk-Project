"""
Корневая конфигурация URL проекта helpdesk_project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("tickets/", include("tickets.urls")),
    path("", RedirectView.as_view(pattern_name="tickets:ticket_list", permanent=False)),
]

if settings.DEBUG:
    # Раздача загруженных файлов (media) напрямую через Django — только для
    # разработки. В продакшене media должен отдавать веб-сервер (nginx и т.п.).
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)