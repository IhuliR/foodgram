from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class TokenAuthSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    error_message = {
        'invalid_credentials': 'Неверный email или пароль.'
    }

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.fail('invalid_credentials')

        if not user.check_password(password):
            self.fail('invalid_credentials')

        if not user.is_active:
            raise serializers.ValidationError('Пользователь удалён.')

        attrs['user'] = user
        return attrs
