import random

from django.db import models
from django.db.models import Exists, OuterRef, Value, BooleanField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

from .constants import (
    ALPHABET,
    MIN_COOKING_TIME,
    MAX_COOKING_TIME,
    MIN_INGREDIENT_AMOUNT,
    MAX_INGREDIENT_AMOUNT,
    MAX_TAG_NAME_LEN,
    MAX_TAG_SLUG_LEN,
    MAX_INGREDIENT_NAME_LEN,
    MAX_MEASUREMENT_UNIT_LEN,
    MAX_RECIPE_NAME_LEN,
    MAX_SHORT_CODE_LEN,
    DEFAULT_SHORT_CODE_LENGTH
)
from .base_models import RecipeForUserBase


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_TAG_NAME_LEN,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=MAX_TAG_SLUG_LEN,
        unique=True,
        verbose_name='Слаг тега',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_INGREDIENT_NAME_LEN,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_MEASUREMENT_UNIT_LEN
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_measurement'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class RecipeQuerySet(models.QuerySet):
    def with_user_flags(self, user):
        if user.is_anonymous:
            return self.annotate(
                is_favorited=Value(False, output_field=BooleanField()),
                is_in_shopping_cart=Value(False, output_field=BooleanField())
            )

        favorited_by = Favorite.objects.filter(
            user=user,
            recipe=OuterRef('pk')
        )
        in_shopping_cart_by = ShoppingCart.objects.filter(
            user=user,
            recipe=OuterRef('pk')
        )

        return self.annotate(
            is_favorited=Exists(favorited_by),
            is_in_shopping_cart=Exists(in_shopping_cart_by)
        )        


class Recipe(models.Model):
    objects = RecipeQuerySet.as_manager()
    name = models.CharField(
        max_length=MAX_RECIPE_NAME_LEN,
        verbose_name='Название'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение'
    )
    text = models.TextField(verbose_name='Текст рецепта')
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_COOKING_TIME),
            MaxValueValidator(MAX_COOKING_TIME)
        ],
        verbose_name='Время приготовления'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    short_code = models.CharField(
        max_length=MAX_SHORT_CODE_LEN,
        unique=True,
        blank=True,
        null=True,
        editable=False,
        verbose_name='Короткий код'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.short_code:
            while True:
                code = self.generate_short_code()
                if not Recipe.objects.filter(short_code=code).exists():
                    self.short_code = code
                    break
        super().save(*args, **kwargs)

    @staticmethod
    def generate_short_code(length=DEFAULT_SHORT_CODE_LENGTH):
        return ''.join(random.choices(ALPHABET, k=length))


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(MIN_INGREDIENT_AMOUNT),
            MaxValueValidator(MAX_INGREDIENT_AMOUNT)
        ]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.recipe} - {self.ingredient} ({self.amount})'


class Favorite(RecipeForUserBase):

    class Meta(RecipeForUserBase.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(RecipeForUserBase):

    class Meta(RecipeForUserBase.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
