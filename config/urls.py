from django.contrib import admin
from django.urls import include, path
from tickets.views import ticket_demo

urlpatterns = [
    # Serve the ticket submission page at the homepage.
    path("", ticket_demo, name="ticket-demo"),
    path("admin/", admin.site.urls),
    path("api/", include("tickets.urls")),
]
