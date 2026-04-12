from django.contrib import admin
from django.db.models import Count

from .models import (
    Recipe,
    Tag,
    Ingredient,
    Favorite,
    ShoppingCart,
    RecipeIngredient
)


class RecipeIngredientInLine(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInLine]
    list_display = (
        'name',
        'author',
        'get_tags'
    )
    search_fields = (
        'name',
        'author__first_name'
    )
    list_filter = ('tags',)
    list_display_links = ('name',)
    readonly_fields = ('favorite_count',)
    filter_horizontal = ('tags',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(favorites_total=Count('favorite_recipe'))

    @admin.display(description='Теги')
    def get_tags(self, obj):
        return ', '.join(tag.name for tag in obj.tags.all())

    @admin.display(description='В избранном')
    def favorite_count(self, obj):
        return obj.favorites_total


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
        'recipes_count'
    )
    search_fields = ('name',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(recipes_total=Count('recipes'))
    
    @admin.display(description='Всего рецептов')
    def recipes_count(self, obj):
        return obj.recipes_total


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'recipes_count'
    )
    search_fields = (
        'name',
        'slug'
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(recipes_total=Count('recipes'))
    
    @admin.display(description='Всего рецептов')
    def recipes_count(self, obj):
        return obj.recipes_total

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__first_name', 'recipe__name')
    list_filter = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__first_name', 'recipe__name')
    list_filter = ('user',)
