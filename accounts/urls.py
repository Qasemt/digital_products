from django.urls import path, include


urlpatterns = [
   # path("accounts/profile/", RegisterView.as_view()),
    path("accounts/", include("allauth.urls")),
]
