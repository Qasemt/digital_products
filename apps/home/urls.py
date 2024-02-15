from django.http import HttpResponse
from django.urls import path
from .views import home_view

urlpatterns = [
    path("", home_view, name="home"),
    path("home/", home_view, name="home"),
]
