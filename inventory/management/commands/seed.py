from django.core.management.base import BaseCommand
from inventory.models import Material


class Command(BaseCommand):
    help = 'Seed initial materials'

    def handle(self, *args, **options):
        data = [
            {
                'material_id': 'M100',
                'name': 'Bolt',
                'model_number': 'B-10',
                'category': 'Hardware',
                'equipment': 'Pump',
                'warehouse': 'WH1',
                'shelf': 'A1',
                'quantity': 100,
            },
            {
                'material_id': 'M101',
                'name': 'Nut',
                'model_number': 'N-5',
                'category': 'Hardware',
                'equipment': 'Valve',
                'warehouse': 'WH1',
                'shelf': 'A2',
                'quantity': 200,
            },
        ]
        for item in data:
            Material.objects.update_or_create(material_id=item['material_id'], defaults=item)
        self.stdout.write('Seeded materials')