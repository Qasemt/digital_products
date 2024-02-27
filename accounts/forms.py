from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from apps.accounts.models import CustomUser


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text="Required. Add a valid email address.")

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].initial = ""

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        try:
            account = CustomUser.c_objects.exclude(pk=self.instance.pk).get(email=email)
        except CustomUser.DoesNotExist:
            return email
        raise forms.ValidationError('Email "%s" is already in use.' % account)


class AccountAuthenticationForm(forms.ModelForm):

    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ("email", "password")

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data["email"]
            password = self.cleaned_data["password"]
            if not authenticate(email=email, password=password):
                raise forms.ValidationError("Invalid login")
