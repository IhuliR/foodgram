from django.shortcuts import redirect

from .models import Recipe


def redirect_short_link(request, code):
    try:
        recipe = Recipe.objects.get(short_code=code)
    except Recipe.DoesNotExist:
        return redirect('/404')
    return redirect(f'/recipes/{recipe.id}/')
