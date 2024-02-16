from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


# class CustomUserManager(BaseUserManager):

#     def create_user(self, email, password=None):
#         """
#         Create and save a user with the given email and password.
#         """
#         if not email:
#             raise ValueError(_("The Email must be set"))
#         email = self.normalize_email(email)
#         user = self.model(email=email)
#         user.set_password(password)
#         user.save()
#         return user

#     def create_superuser(self, email, password=None):
#         SUPO = self.create_user(email, password)
#         SUPO.is_staff = True
#         SUPO.is_superuser = True
#         SUPO.save()
#         return SUPO
