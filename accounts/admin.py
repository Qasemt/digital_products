from django.contrib import admin
from .models import Profile, CustomUser
from django.contrib.auth.admin import UserAdmin


# class CustomUserAdmin(UserAdmin):
#     list_display = (
#         "email",
#         "username",
#         "date_joined",
#         "last_login",
#         "is_admin",
#         "is_staff",
#         "is_superuser",
#     )
#     search_fields = ("email", "username")
#     readonly_fields = ("date_joined", "last_login")
#     filter_horizontal = ()
#     list_filter = ()
#     fieldsets = ()


class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        "CustomUser",
        "first_name",
        "last_name",
        "birthday",
        "mobile_number",
    ]


admin.site.register(CustomUser)
admin.site.register(Profile, ProfileAdmin)
