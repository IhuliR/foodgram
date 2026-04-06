from django.contrib import admin

from .models import Recipe, Tag, Ingredient, Favorite, ShoppingCart


class RecipeAdmin(admin.ModelAdmin):
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

    @admin.display(description='Теги')
    def get_tags(self, obj):
        return ', '.join(tag.name for tag in obj.tags.all())

    @admin.display(description='В избранном')
    def favorite_count(self, obj):
        return obj.favorited_by.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug'
    )
    search_fields = (
        'name',
        'slug'
    )


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__first_name', 'recipe__name')
    list_filter = ('user',)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__first_name', 'recipe__name')
    list_filter = ('user',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
