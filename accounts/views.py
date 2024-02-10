from django.http import HttpResponse
from django.shortcuts import redirect, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.forms import AccountAuthenticationForm
from .models import Profile
from .serializers import ProfileSerializer
from django.contrib.auth import login, authenticate, logout


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


def logout_view(request):
    logout(request)
    return redirect("home")


def get_redirect_if_exists(request):
    redirect = None
    if request.GET:
        if request.GET.get("next"):
            redirect = str(request.GET.get("next"))
    return redirect


def home_view(request):
    return render(request, "home.html", {})
