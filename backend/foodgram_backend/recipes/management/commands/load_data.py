import csv

from django.core.management.base import BaseCommand
from django.conf import settings

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт ингредиентов из CSV'

    def handle(self, *args, **kwargs):
        file_path = settings.DATA_DIR / 'ingredients.csv'
        self.load_ingredients(file_path)

    def load_ingredients(self, file_path):
        created_count = 0
        skipped_count = 0

        with open(file_path, encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) != 2:
                    continue
                name, unit = row
                obj, created = Ingredient.objects.get_or_create(
                    name=name.strip(),
                    measurement_unit=unit.strip(),
                )
                if created:
                    created_count += 1
                else:
                    skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'ОК. Создано: {created_count}, пропущено: {skipped_count}'
            )
        )
