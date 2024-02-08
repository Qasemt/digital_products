from django.urls import path
from .views import ProfileAPIView

urlpatterns = [
    path('accounts/profiles/', ProfileAPIView.as_view(), name='profile-list'),
    path('accounts/profile/<int:pk>', ProfileAPIView.as_view(), name='profile-list'),
]