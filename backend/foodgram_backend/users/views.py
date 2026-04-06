from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .serializers import TokenAuthSerializer


class AuthViewSet(viewsets.ViewSet):
    """Кастомный вьюсет для логина и логаута по токену"""

    @action(
        detail=False,
        methods=['post'],
        url_path='login'
    )
    def login(self, request):
        serializer = TokenAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {'auth_token': token.key},
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=['post'],
        url_path='logout'
    )
    def logout(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action == 'login':
            return [AllowAny()]
        return [IsAuthenticated()]
