from django.urls import path

from . import views

app_name = "tickets"

urlpatterns = [
    path("", views.TicketListView.as_view(), name="ticket_list"),
    path("dashboard/", views.AdminDashboardView.as_view(), name="admin_dashboard"),
    path("create/", views.TicketCreateView.as_view(), name="ticket_create"),
    path("<int:pk>/", views.TicketDetailView.as_view(), name="ticket_detail"),
    path("<int:pk>/status/", views.TicketStatusUpdateView.as_view(), name="ticket_status_update"),
    path("<int:pk>/delete/", views.TicketDeleteView.as_view(), name="ticket_delete"),
    path("<int:pk>/comment/", views.CommentCreateView.as_view(), name="comment_create"),
    path("<int:pk>/attachment/", views.AttachmentCreateView.as_view(), name="attachment_create"),
]