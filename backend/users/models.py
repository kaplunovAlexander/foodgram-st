from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, EmailValidator
from django.db import models


NAME_VALIDATOR = RegexValidator(
    regex=r'^[А-Яа-яA-Za-z\- ]+$',
    message='Поле может содержать только буквы, пробел и дефис'
)

USERNAME_VALIDATOR = RegexValidator(
    regex=r'^[a-zA-Z0-9._-]+$',
    message=(
        'Имя пользователя может содержать только латинские буквы, '
        'цифры, дефис, подчёркивание и точку'
    )
)


class User(AbstractUser):
    first_name = models.CharField(
        max_length=150, verbose_name='Имя', validators=[NAME_VALIDATOR]
    )
    last_name = models.CharField(
        max_length=150, verbose_name='Фамилия', validators=[NAME_VALIDATOR]
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Имя пользователя',
        validators=[USERNAME_VALIDATOR]
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Электронная почта',
        validators=[
            EmailValidator(
                message='Введите корректный адрес электронной почты.')
        ]
    )
    avatar = models.ImageField(upload_to='users/', null=True, default=None)

    def __str__(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.username

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers'
    )

    class Meta:
        unique_together = ('user', 'author')
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
