from django.contrib import admin
from django.urls import include, path

# to deal with tickets/....
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("tickets.urls")),
]