from django.core.management.base import BaseCommand
from mainapp.models import Return


class Command(BaseCommand):
    help = "All return requests must be refused."

    def handle(self, *args, **options):
        if Return.objects.exists(): 
            Return.objects.all().delete()
        print('returns are clear')