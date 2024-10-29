from django.core.management.base import BaseCommand
from api.models import Topico  # Adjust the import based on your app structure

class Command(BaseCommand):
    help = 'Remove all items from the Topico table'

    def handle(self, *args, **kwargs):
        # Count how many Topico entries there are before deletion
        count = Topico.objects.count()

        # Delete all Topico entries
        Topico.objects.all().delete()

        # Print a success message
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} Topico entries.'))
