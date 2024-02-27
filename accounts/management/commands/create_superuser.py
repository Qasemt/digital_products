from django.core.management.base import BaseCommand

from apps.accounts.models import CustomUser

class Command(BaseCommand):
    help = 'Create a default superuser after migrations.'

    def handle(self, *args, **options):
        # Check if a superuser already exists
        if not CustomUser.c_objects.filter(is_superuser=True).exists():
            # Create a new superuser
            CustomUser.c_objects.create_superuser(
                password='1234',
                email='rayreadeer@gmail.com'
            )
            self.stdout.write(self.style.SUCCESS('Default superuser created.'))
        else:
            self.stdout.write(self.style.NOTICE('A superuser already exists. Skipping creation.'))