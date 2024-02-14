from django.http import HttpResponse
from django.urls import path
from .views import ChangePassword, ForgetPassword, ProfileAPIView, login_view, logout_view, register_view, user_verify

urlpatterns = [
    # path("", lambda request: HttpResponse("Hello, World!"), name="hello_world"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/", register_view, name="register"),
    path("verify/<email_token>", user_verify, name="verify"),
    path("forget_password/", ForgetPassword, name="forget_password"),
    path("change_password/<token>/", ChangePassword.as_view(), name="change_password"),
    path("accounts/profiles/", ProfileAPIView.as_view(), name="profile-list"),
    path("accounts/profile/<int:pk>", ProfileAPIView.as_view(), name="profile-list"),
]
