from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("quotes.urls", namespace="quotes")),
    path("admin/", admin.site.urls),
    ]