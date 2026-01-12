from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create default admin user'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'admin'
        password = 'admin123'
        email = 'admin@example.com'
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write('Created admin user')
        else:
            self.stdout.write('Admin user already exists')