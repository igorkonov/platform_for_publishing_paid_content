from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    """Команда для загрузки фикстуры"""
    def handle(self, *args, **options):
        call_command('loaddata', 'fixtures.json')
