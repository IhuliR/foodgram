from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class RecipeForUserBase(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s_user'
    )
    recipe = models.ForeignKey(
        'recipes.Recipe',
        on_delete=models.CASCADE,
        related_name='%(class)s_recipe'
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_%(class)s_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user} -> {self.recipe}'
