from django.core.management.base import BaseCommand
from users import services


class Command(BaseCommand):
    help = 'generate dummy hostess data'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=100)

    def handle(self, *args, **options):
        count = options['count']
        service = services.HostessService()
        service.generate_dummy_hostess(count=count)
        self.stdout.write(self.style.SUCCESS('super user was created successfully'))