from django.urls import path
from .views import ProfileAPIView, home_view, login_view, logout_view

urlpatterns = [
    path("accounts/profiles/", ProfileAPIView.as_view(), name="profile-list"),
    path("accounts/profile/<int:pk>", ProfileAPIView.as_view(), name="profile-list"),
]
