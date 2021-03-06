from django.core.management.base import BaseCommand
from django.conf import settings
from users import models


class Command(BaseCommand):
    help = 'Create new superuser to login admin console'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, default=settings.SUPERUSER_EMAIL)
        parser.add_argument('--password', type=str, default=settings.SUPERUSER_PASSWORD)


    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        try:
            user = models.User.objects.get(email=email)
        except models.User.DoesNotExist:
            user = models.User.objects.create_user(email, email, password)
        group, created = models.Group.objects.get_or_create(title="CABABA公式", name="CABABA公式")
        user.user_type = models.User.UserTypes.STAFF
        user.is_superuser = True
        user.is_staff = True
        user.group = group
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS('super user was created successfully'))