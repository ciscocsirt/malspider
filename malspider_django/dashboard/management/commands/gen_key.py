from django.utils.crypto import get_random_string
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Creates a new SECRET_KEY for use in the Django settings.py file.'

    def handle(self, *args, **options):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        SECRET_KEY = get_random_string(50, chars)
        print SECRET_KEY
