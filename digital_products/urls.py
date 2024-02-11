import os
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from accounts.views import login_view, logout_view, home_view, register_view, ForgetPassword, ChangePassword, user_verify
from digital_products.settings import BASE_DIR

urlpatterns = [
    path("", home_view, name="home"),
    path("admin/", admin.site.urls),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/", register_view, name="register"),
    path("verify/<email_token>", user_verify, name="verify"),
    path("password_reset/", home_view, name="password_reset"),
    path("forget_password/", ForgetPassword, name="forget_password"),
    path("change_password/<token>/", ChangePassword.as_view(), name="change_password"),
    # path("", include("accounts.urls")),
    # path("", include("products.urls")),
]


if settings.IS_DEVEL:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
