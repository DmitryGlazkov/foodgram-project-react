from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from users.constants import EMAIL_MAX_LENGTH, USER_DATA_MAX_LENGTH


class User(AbstractUser):
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        verbose_name='Адрес электронной почты',
        help_text='Укажите адрес Вашей электронной почты',
    )
    username = models.CharField(
        max_length=USER_DATA_MAX_LENGTH,
        unique=True,
        verbose_name='Уникальный юзернейм',
        help_text='Укажите уникальный юзернейм',
        validators=[
            RegexValidator(
                r'^[\w.@+-]+\Z',
                'Имя пользователя содержит недопустимые символы.'
            )],
    )
    first_name = models.CharField(
        max_length=USER_DATA_MAX_LENGTH,
        verbose_name='Имя',
        help_text='Укажите Ваше имя',
    )
    last_name = models.CharField(
        max_length=USER_DATA_MAX_LENGTH,
        verbose_name='Фамилия',
        help_text='Укажите Вашу фамилию',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор рецепта',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = (('user', 'author'),)

    def __str__(self):
        return f'{self.user} подписчик - {self.author}'
