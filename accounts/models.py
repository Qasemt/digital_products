from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    birthday = models.DateField()
    mobile_number = models.CharField(max_length=20)
    image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return self.user.username
    
    #ّبرای حذف عکس قدیمی اگر عوض کرده باشد.
    def save(self, *args, **kwargs):
         
        if self.pk:
            
            current_profile = Profile.objects.get(pk=self.pk)
           
            if current_profile.image and self.image != current_profile.image:
                # Delete the old image from storage
                if default_storage.exists(current_profile.image.name):
                    default_storage.delete(current_profile.image.name)

        super().save(*args, **kwargs)

    class Meta:
        db_table = 'profiles'
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        ordering = ['last_name', 'name']