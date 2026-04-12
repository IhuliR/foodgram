from django.contrib.auth import get_user_model
from django.db.models import Sum, Exists, OuterRef, Value, BooleanField
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from .serializers import (
    UserReadSerializer,
    SubscriptionSerializer,
    AvatarSerializer,
    IngredientSerializer,
    TagSerializer,
    RecipeReadSerializer,
    RecipeCreateSerializer,
    RecipeSmallSerializer,
)
from .permissions import IsAuthorOrReadOnly
from .filters import IngredientFilter, RecipeFilter
from .pagination import PageSizePagination
from recipes.models import (
    Ingredient,
    Tag,
    Favorite,
    Recipe,
    ShoppingCart,
    RecipeIngredient,
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


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    pagination_class = PageSizePagination

    def get_serializer_class(self):
        if self.action in ('subscriptions', 'subscribe'):
            return SubscriptionSerializer
        if self.action == 'avatar':
            return AvatarSerializer
        if self.action in ('list', 'retrieve', 'me'):
            return UserReadSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in (
            'me',
            'avatar',
            'subscriptions',
            'subscribe',
            'set_password'
        ):
            return [IsAuthenticated()]
        return super().get_permissions()

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
    def subscribe(self, request, *args, **kwargs):
        author = self.get_object()
        user = request.user

        if user == author:
            return Response(
                {'errors': 'Нельзя подписаться на себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            subscription, created = Subscription.objects.get_or_create(
                user=user,
                author=author
            )

            if not created:
                return Response(
                    {'errors': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted_count, _ = Subscription.objects.filter(
            user=user,
            author=author
        ).delete()

        if deleted_count == 0:
            return Response(
                {'errors': 'Подписка не найдена'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeReadSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = PageSizePagination
    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly)
    queryset = Recipe.objects.all().order_by('-pub_date')

    def get_queryset(self):
        queryset = Recipe.objects.all().order_by('-pub_date')
        user = self.request.user

        if user.is_anonymous:
            return queryset.annotate(
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

        return queryset.annotate(
            is_favorited=Exists(favorited_by),
            is_in_shopping_cart=Exists(in_shopping_cart_by)
        )

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer
        return super().get_serializer_class()

    def handle_user_recipe_relation(self, request, model):
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            _, created = model.objects.get_or_create(
                user=user,
                recipe=recipe
            )

            if not created:
                return Response(
                    {'errors': 'Рецепт уже был в списке'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = self.get_serializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted_count, _ = model.objects.filter(
            user=user,
            recipe=recipe
        ).delete()

        if deleted_count == 0:
            return Response(
                {'errors': 'Элемент не найден.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    def _update_and_serialize(self, request, partial=False):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()

        recipe = self.get_queryset().get(pk=recipe.pk)
        read_serializer = RecipeReadSerializer(
            recipe,
            context={'request': request}
        )

        return Response(read_serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()

        recipe = self.get_queryset().get(pk=recipe.pk)
        read_serializer = RecipeReadSerializer(
            recipe,
            context={'request': request}
        )
        headers = self.get_success_headers(read_serializer.data)

        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        return self._update_and_serialize(request, partial=False)

    def partial_update(self, request, *args, **kwargs):
        return self._update_and_serialize(request, partial=True)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated],
        serializer_class=RecipeSmallSerializer
    )
    def shopping_cart(self, request, pk=None):
        return self.handle_user_recipe_relation(request, ShoppingCart)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='favorite',
        permission_classes=[IsAuthenticated],
        serializer_class=RecipeSmallSerializer
    )
    def favorite(self, request, pk=None):
        return self.handle_user_recipe_relation(request, Favorite)

    @action(
        detail=False,
        methods=('get',),
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcart_recipe__user=request.user
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
        url_path='get-link',
        permission_classes=[AllowAny]
    )
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        if not recipe.short_code:
            recipe.save()
        short_link = request.build_absolute_uri(f'/s/{recipe.short_code}/')
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)
