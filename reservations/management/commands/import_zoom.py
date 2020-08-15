from django.core.management.base import BaseCommand
from django.conf import settings

from reservations import services


class Command(BaseCommand):
    help = 'Create new superuser to login admin console'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str)


    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        filepath = options["excel_file"]
        service = services.ZoomService()
        service.import_accounts(filepath)
        self.stdout.write(self.style.SUCCESS('Zoom accounts was imported successfully'))