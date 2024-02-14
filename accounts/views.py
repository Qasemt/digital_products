import json
import uuid
from enum import IntEnum
from django.http import HttpResponse, HttpResponseRedirect
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
from django.core.cache import cache


#:::::::::: Modelsss
class ActionType(IntEnum):
    FORGET_PASSWORD = 1
    VERIFYING_EMAIL = 2


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
                profile_obj = Profile.objects.filter(CustomUser=user).first()
                if not user.is_superuser and not profile_obj.is_email_verified:
                    messages.warning(request, "Your account is not verified. please check your mail.")
                    return redirect("login")

                login(request, user)
                if destination:
                    return redirect(destination)
                return redirect("home")
        else:
            message = "Email Not Valid"
            messages.error(request, message)
            context = {"message": message}
            return render(request, "login.html", context)

    else:
        form = AccountAuthenticationForm()

    context["login_form"] = form

    return render(request, "login.html", context)


def register_view(request, *args, **kwargs):

    if request.method == "POST":
        global username
        global email

        email = request.POST.get("email")
        pass1 = request.POST.get("password1")
        pass2 = request.POST.get("password2")

        if CustomUser.objects.filter(email=email).first():
            messages.warning(request, "Username is already taken")
            return HttpResponseRedirect(request.path_info)

        if CustomUser.objects.filter(email=email).first():
            messages.warning(request, "Email is already taken")
            return HttpResponseRedirect(request.path_info)

        if pass1 != pass2:
            messages.warning(request, "Both passwords should match!")
            return HttpResponseRedirect(request.path_info)

        user_obj = CustomUser.objects.create_user(email=email, password=pass1)
        user_obj.save()
        email_token = str(uuid.uuid4())

        m = ActionPassword(email, type_action=ActionType.VERIFYING_EMAIL)
        json_string = m.to_json()
        cache.set(email_token, json_string, 3600)  # Cache the data for 10 minute

        send_mail_after_signup(email, email_token)
        messages.success(request, "Email has been sent to verify your account!")
        return redirect("register")

    return render(request, "register.html")


def get_redirect_if_exists(request):
    redirect = None
    if request.GET:
        if request.GET.get("next"):
            redirect = str(request.GET.get("next"))
    return redirect


import uuid


# for verifying email
def send_mail_after_signup(email, email_token):
    subject = "Action Needed!!! Your account needs to be verify!"

    if settings.IS_DEVEL:
        message = f"Please click on the link to verify your account. http://127.0.0.1:8000/verify/{email_token}"
    else:
        message = f"Please click on the link to verify your account. https://{settings.DOMAIN_NAME}/verify/{email_token}"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)


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
            messages.error(request, "Token is invalid.")
            return redirect("login")

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
            return HttpResponse(f"has been error {str(e)}")


def user_verify(request, email_token):

    try:
        cached_data = cache.get(key=email_token)
        model_instance = {}
        if cached_data:
            model_instance = json.loads(cached_data)
        else:
            messages.error(request, "token not valid ")
            return redirect("login")

        user = CustomUser.objects.filter(email=model_instance["email"]).first()
        profile_obj = user.profile
        if profile_obj:
            if profile_obj.is_email_verified:
                messages.info(request, "Your account is already verified.")
                print(messages)
                return redirect("login")

            profile_obj.is_email_verified = True
            profile_obj.save()
            subject = f"!! New User Registered In {settings.APP_NAME} !!"
            message = f"""Hi , We have noticed that new user is registered in your  {settings.APP_NAME} Authentication System .
            Details of user -  Email - {user.email}
             """
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL])
            messages.success(request, "Your account has been verified. Now you can login.")
            return redirect("login")
        else:
            return redirect("error")
    except Exception as e:
        print(e)
        return render(request, "login.html")
    # return render(request, 'verify.html')
