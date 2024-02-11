from enum import IntEnum
import json
from django.forms import ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.forms import AccountAuthenticationForm, RegistrationForm
from .models import Profile
from .serializers import ProfileSerializer
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .models import CustomUser
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder


#:::::::::: Modelsss
class ActionType(IntEnum):
    FORGET_PASSWORD = 1
    CHANGE_PASSWORD = 2


class ActionPassword:

    def __init__(self, email, type_action: ActionType):
        self.email = email
        self.type_action = type_action

    def to_json(self):
        return json.dumps(self.__dict__)


class ProfileAPIView(APIView):
    def get(self, request):
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        if pk is not None:
            try:
                profile = Profile.objects.get(pk=pk)
            except Profile.DoesNotExist:
                return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

            serializer = ProfileSerializer(profile, context={"request": request})
            return Response(serializer.data)
        else:
            profiles = Profile.objects.all()
            serializer = ProfileSerializer(profiles, many=True, context={"request": request})
            return Response(serializer.data)

    def put(self, request, pk=None):
        if pk is not None:
            profile = self.get_profile(pk)
            if profile is None:
                return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
            serializer = ProfileSerializer(profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Invalid request."}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        if pk is not None:
            profile = self.get_profile(pk)
            if profile is None:
                return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
            profile.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "Invalid request."}, status=status.HTTP_400_BAD_REQUEST)


def logout_view(request):
    logout(request)
    return redirect("home")


def login_view(request, *args, **kwargs):
    context = {}

    user = request.user
    if user.is_authenticated:
        return redirect("home")

    destination = get_redirect_if_exists(request)
    print("destination: " + str(destination))

    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST["email"]
            password = request.POST["password"]
            user = authenticate(email=email, password=password)

            if user:
                login(request, user)
                if destination:
                    return redirect(destination)
                return redirect("home")

    else:
        form = AccountAuthenticationForm()

    context["login_form"] = form

    return render(request, "login.html", context)


def register_view(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
        return HttpResponse("You are already authenticated as " + str(user.email))

    context = {}
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get("email").lower()
            raw_password = form.cleaned_data.get("password1")
            account = authenticate(email=email, password=raw_password)
            login(request, account)
            destination = kwargs.get("next")
            if destination:
                return redirect(destination)
            return redirect("home")
        else:
            context["registration_form"] = form

    else:
        form = RegistrationForm()
        context["registration_form"] = form
    return render(request, "register.html", context)


def get_redirect_if_exists(request):
    redirect = None
    if request.GET:
        if request.GET.get("next"):
            redirect = str(request.GET.get("next"))
    return redirect


def home_view(request):
    return render(request, "home.html", {})


import uuid


# for sending forget password link
def send_forget_password_mail(email, token):
    subject = "Digital Products (Your forget password link)"
    if settings.IS_DEVEL:
        message = f"Hi , click on the link to reset your password http://127.0.0.1:8000/change_password/{token}/"
    else:
        message = f"Hi , click on the link to reset your password https://{settings.DOMAIN_NAME}/change_password/{token}/"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True


# https://github.com/Prajwalkamde/django_authentication_with_email_verify/blob/master/app/views.py
def ForgetPassword(request):

    try:
        if request.method == "POST":
            email = request.POST.get("email")

            if not CustomUser.objects.filter(email=email).first():
                messages.warning(request, "Not user found with this email.")
                return redirect("/forget_password/")

            token = str(uuid.uuid4())
            m = ActionPassword(email, type_action=ActionType.FORGET_PASSWORD)
            json_string = m.to_json()
            cache.set(token, json_string, 3600)  # Cache the data for 10 minute

            send_forget_password_mail(email, token)
            messages.success(request, "An email is sent to reset your password.")
            return redirect("/forget_password/")

    except Exception as e:
        error_message = f"Bad Request: {str(e)}"
        messages.warning(request, error_message)
        return redirect("/forget_password/")

    return render(request, "forget_password.html")


class ChangePassword(APIView):
    def get(self, request, token):

        context = {}
        cached_data = cache.get(key=token)
        if cached_data:
            model_instance = json.loads(cached_data)
            context = {"user_pk": model_instance["email"]}
        else:
            messages.warning(request, "Token not valid.")
            context = {"error_messages": messages.get_messages(request)}

        return render(request, "change_password.html", context)

    def post(self, request, token):
        try:
            user_pk = request.data.get("user_pk")

            if user_pk is None:
                messages.warning(request, "No user id found.")
                return redirect(f"/change_password/{token}/")

            user_obj = CustomUser.objects.filter(email=user_pk).first()
            if not user_obj:
                messages.warning(request, "No user pk found.")
                return redirect(f"/change_password/{token}/")

            new_password = request.POST.get("new_password")
            confirm_new_password = request.POST.get("confirm_new_password")

            if new_password != confirm_new_password:
                messages.warning(request, "Both passwords should  be equal!")
                return redirect(f"/change_password/{token}/")

            user_obj.set_password(new_password)
            user_obj.save()
            messages.success(request, "Your password has been changed. login with new password")
            return redirect("login")

        except Exception as e:
            messages.error(request, str(e))
            context = {"error_messages": messages.get_messages(request)}
            return render(request, "change_password.html", context)


def user_verify(request, email_token):

    try:
        cached_data = cache.get(key=email_token)

        if cached_data:
            model_instance = json.loads(cached_data)
        else:
            messages.info(request, "Your account is already verified.")
            print(messages)
            return redirect("login")

        profile_obj = Profile.objects.filter(email=email_token).first()
        if profile_obj:
            if profile_obj.is_email_verified:
                messages.info(request, "Your account is already verified.")
                print(messages)
                return redirect("login")

            profile_obj.is_email_verified = True
            profile_obj.save()
            subject = f"!! New User Registered In Django Authentication !!"
            message = f"""Hi Prajwal, We have noticed that new user is registered in your Django Authentication System .
            Details of user -  Email - {model_instance.email}
            You can check user details from here - https://django-auth-v46x.onrender.com/superadmin/ """
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL])
            messages.success(request, "Your account has been verified. Now you can login.")
            return redirect("login")
        else:
            return redirect("error")
    except Exception as e:
        print(e)
        return render(request, "login.html")
    # return render(request, 'verify.html')
