from django.core.management.base import BaseCommand
from mainapp.models import Return


class Command(BaseCommand):
    help = "All return requests must be refused."

    def handle(self, *args, **options):
        returns = Return.objects.all()
        if returns:
            returns.delete()
        print('returns are clear')