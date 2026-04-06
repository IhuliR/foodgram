from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import AuthViewSet
from .views import (
    RecipeViewSet,
    IngredientViewSet,
    TagViewSet,
    UserViewSet,
)


login_view = AuthViewSet.as_view({'post': 'login'})
logout_view = AuthViewSet.as_view({'post': 'logout'})

auth_patterns = [
    path('token/login/', login_view, name='token-login'),
    path('token/logout/', logout_view, name='token-logout')
]

router = DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('users', UserViewSet, basename='users')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('auth/', include(auth_patterns)),
    path('', include(router.urls))
]
