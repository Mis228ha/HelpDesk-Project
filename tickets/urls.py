from django.urls import path

from . import views

app_name = "tickets"

urlpatterns = [
    path("", views.TicketListView.as_view(), name="ticket_list"),
    path("create/", views.TicketCreateView.as_view(), name="ticket_create"),
    path("<int:pk>/", views.TicketDetailView.as_view(), name="ticket_detail"),
    path("<int:pk>/status/", views.TicketStatusUpdateView.as_view(), name="ticket_status_update"),
    path("<int:pk>/comment/", views.CommentCreateView.as_view(), name="comment_create"),
]