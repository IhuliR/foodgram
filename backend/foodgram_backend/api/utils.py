import string
import random

from recipes.models import ShortLink

ALPHABET = string.ascii_letters + string.digits


def generate_code(length=6):
    return ''.join(random.choice(ALPHABET) for _ in range(length))


def get_or_create_short_link(recipe):
    obj, created = ShortLink.objects.get_or_create(recipe=recipe)

    if created:
        while True:
            code = generate_code()
            if not ShortLink.objects.filter(code=code).exists():
                obj.code = code
                obj.save()
                break

    return obj.code
