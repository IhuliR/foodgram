from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .serializers import (
    UserReadSerializer,
    UserCreateSerializer,
    SubscriptionSerializer,
    AvatarSerializer,
    IngredientSerializer,
    TagSerializer,
    RecipeReadSerializer,
    RecipeCreateSerializer,
    RecipeSmallSerializer,
    SetPasswordSerializer
)
from .permissions import IsAuthor
from .utils import get_or_create_short_link
from .filters import IngredientFilter, RecipeFilter
from .pagination import PageSizePagination
from recipes.models import (
    Ingredient,
    Tag,
    Favorite,
    Recipe,
    ShoppingCart,
    RecipeIngredient,
    ShortLink
)
from users.models import Subscription


User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (AllowAny,)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = User.objects.all()
    pagination_class = PageSizePagination
    AUTH_REQUIRED_ACTIONS = (
        'me',
        'avatar',
        'subscriptions',
        'set_password',
        'subscribe'
    )

    @action(
        detail=False,
        methods=('post',),
        url_path='set_password',
    )
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        url_path='me',
    )
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=('put', 'delete'),
        url_path='me/avatar'
    )
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=False
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        if user.avatar:
            user.avatar.delete(save=False)
        user.avatar = None
        user.save(update_fields=['avatar'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        authors = User.objects.filter(subscribers__user=request.user)
        page = self.paginate_queryset(authors)
        serializer = self.get_serializer(
            page if page is not None else authors,
            many=True
        )
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='subscribe'
    )
    def subscribe(self, request, pk=None):
        author = self.get_object()
        user = request.user

        if request.method == 'POST':
            if user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            Subscription.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = Subscription.objects.filter(
            user=user,
            author=author
        ).first()
        if not subscription:
            return Response(
                {'errors': 'Подписка не найдена'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if self.action in ('subscriptions', 'subscribe'):
            return SubscriptionSerializer
        if self.action == 'avatar':
            return AvatarSerializer
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        return UserReadSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        if self.action in self.AUTH_REQUIRED_ACTIONS:
            return [IsAuthenticated()]
        return [AllowAny()]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().distinct()
    serializer_class = RecipeReadSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = PageSizePagination
    queryset = Recipe.objects.all().order_by('-pub_date')

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer
        if self.action in ('favorite', 'shopping_cart'):
            return RecipeSmallSerializer
        return RecipeReadSerializer

    def get_permissions(self):
        if self.action in (
            'create',
            'favorite',
            'shopping_cart',
            'download_shopping_cart'
        ):
            return [IsAuthenticated()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsAuthor()]
        return [AllowAny()]

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже в списке'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = self.get_serializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        shopping_cart = ShoppingCart.objects.filter(
            user=user,
            recipe=recipe
        ).first()
        if not shopping_cart:
            return Response(
                {'errors': 'Элемент не найден'},
                status=status.HTTP_400_BAD_REQUEST
            )
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='favorite',
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Вы уже добавили этот рецепт в избранное'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = self.get_serializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        favorite = Favorite.objects.filter(
            user=user,
            recipe=recipe
        ).first()
        if not favorite:
            return Response(
                {'errors': 'Рецепт не найден в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )

        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__in_shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        lines = ['Список покупок:\n\n']

        for ingredient in ingredients:
            lines.append(
                f'{ingredient["ingredient__name"]}'
                f'({ingredient["ingredient__measurement_unit"]}) - '
                f'{ingredient["total_amount"]}\n'
            )
        response = HttpResponse(
            ''.join(lines),
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    @action(
        detail=True,
        methods=('get',),
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        code = get_or_create_short_link(recipe)
        short_link = request.build_absolute_uri(f'/s/{code}/')
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)


def redirect_short_link(request, code):
    link = get_object_or_404(ShortLink, code=code)
    return redirect(f'/recipes/{link.recipe.id}/')
