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

        with open(file_path, encoding='utf-8') as f:
            reader = csv.reader(f)
            ingredients = []

            for row in reader:
                if len(row) != 2:
                    continue
                name, unit = row
                ingredients.append(
                    Ingredient(
                        name=name.strip(),
                        measurement_unit=unit.strip(),
                    )
                )
        Ingredient.objects.bulk_create(
            ingredients,
            ignore_conflicts=True
        )

        self.stdout.write(
            self.style.SUCCESS(
                'Успешно!'
            )
        )
