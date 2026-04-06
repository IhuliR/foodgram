from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import username_validator
from .constants import MAX_EMAIL_LEN, MAX_USERNAME_LEN


class User(AbstractUser):
    username = models.CharField(
        unique=True,
        max_length=MAX_USERNAME_LEN,
        validators=[username_validator,],
        verbose_name='Юзернейм'
    )
    bio = models.TextField('Биография', blank=True)
    avatar = models.ImageField(
        upload_to='users/',
        null=True,
        blank=True,
        verbose_name='Аватар'
    )
    email = models.EmailField(
        unique=True,
        max_length=MAX_EMAIL_LEN,
        verbose_name='Почта'
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Имя'
    )

    def __str__(self):
        return self.first_name

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    def __str__(self):
        return f'{self.user} -> {self.author}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            ),
            models.CheckConstraint(
                condition=~models.Q(user=models.F('author')),
                name='prevent_self_subscription'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
