import re

from django.core.exceptions import ValidationError


USERNAME_RE = re.compile(r'[\w.@+-]+\Z')


def username_validator(value):
    """Валидация для username: Разрешает использование только [\\w.@+-]."""

    if not USERNAME_RE.match(value):
        invalid_chars = re.sub(r'[\w.@+-]', '', value)
        invalid_unique = ''.join(sorted(set(invalid_chars)))

        raise ValidationError(
            f'Использование {invalid_unique} в username недопустимо.'
        )
    return value
