from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
import re

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    birthday = models.DateField(null=True)
    mobile_number = models.CharField(max_length=20,)
    image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_time = models.DateTimeField(_('create time'),auto_now_add=True)
    updated_time = models.DateTimeField(_('update time'),auto_now=True)

    
    def __str__(self):
        return self.user.username

    class Meta:
        db_table = _('profiles')
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')
        ordering = ['last_name', 'name']


    def clean(self):
        # Validate the mobile_number field
        if self.mobile_number:
            pattern = r'^\+[0-9]{12}$'  # Regex pattern for the format +989359445555
            if not re.match(pattern, self.mobile_number):
                raise ValidationError('Mobile number should be in the format +989359445555')
            
    #ّبرای حذف عکس قدیمی اگر عوض کرده باشد.
    def save(self, *args, **kwargs):
         
        if self.pk:
            
            current_profile = Profile.objects.get(pk=self.pk)
           
            if current_profile.image and self.image != current_profile.image:
                # Delete the old image from storage
                if default_storage.exists(current_profile.image.name):
                    default_storage.delete(current_profile.image.name)

        super().save(*args, **kwargs)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


