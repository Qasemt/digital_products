from django.db import models
from django.core.files.storage import default_storage
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
import re
from django.contrib.auth.models import AbstractBaseUser
from digital_products import settings
from .managers import CustomUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Please provide email")

        ne = self.normalize_email(email)
        UPO = self.model(email=ne)
        UPO.set_password(password)
        UPO.save()

        return UPO

    def create_superuser(self, email, password):
        SUPO = self.create_user(email, password)
        SUPO.is_staff = True
        SUPO.is_superuser = True
        SUPO.save()
        return SUPO


# ____ USER ___________
class CustomUser(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(primary_key=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS = ["first_name", "last_name"]

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


# ======== profile
class Profile(models.Model):
    CustomUser = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    is_email_verified = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    birthday = models.DateField(null=True)
    mobile_number = models.CharField(
        max_length=20,
    )

    image_url = models.ImageField(upload_to="profiles/", blank=True, null=True)
    created_time = models.DateTimeField(_("create time"), auto_now_add=True)
    updated_time = models.DateTimeField(_("update time"), auto_now=True)

    def __str__(self):
        return self.CustomUser.email

    class Meta:
        db_table = _("profiles")
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        ordering = ["last_name", "first_name"]

    def clean(self):
        # Validate the mobile_number field
        if self.mobile_number:
            # Regex pattern for the format +989359445555
            pattern = r"^\+[0-9]{12}$"
            if not re.match(pattern, self.mobile_number):
                raise ValidationError("Mobile number should be in the format +989359445555")

    # ّبرای حذف عکس قدیمی اگر عوض کرده باشد.
    def save(self, *args, **kwargs):
        if self.CustomUser.email:
            # Generate a unique filename for the image using the email
            filename = f"{self.CustomUser.email}.jpg"
            self.image_url.name = filename

        if self.pk:

            current_profile = Profile.objects.get(pk=self.pk)

            if current_profile.image_url and self.image_url != current_profile.image_url:
                # Delete the old image from storage
                if default_storage.exists(current_profile.image_url.name):
                    default_storage.delete(current_profile.image_url.name)

        super().save(*args, **kwargs)
