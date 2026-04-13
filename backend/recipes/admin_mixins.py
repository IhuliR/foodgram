from django.contrib import admin
from django.db.models import Count


class RecipesCountAdminMixin:

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(recipes_total=Count('recipes'))

    @admin.display(description='Всего рецептов')
    def recipes_count(self, obj):
        return obj.recipes_total
