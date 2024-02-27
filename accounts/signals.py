from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Profile
from rest_framework.response import Response
from rest_framework import status


@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(CustomUser=instance)


@receiver(post_save, sender=CustomUser)
def save_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        return Response(
            {"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND
        )
