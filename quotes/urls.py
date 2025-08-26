from django.urls import path
from . import views

app_name = "quotes"

urlpatterns = [
    path("", views.random_quote_view, name="random"),
    path("add/", views.add_quote_view, name="add"),
    path("<int:pk>/vote/", views.vote_view, name="vote"),
    path("top/", views.top_view, name="top"),
    path("search/", views.search_view, name="search")
]