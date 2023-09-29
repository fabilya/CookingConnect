from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import (ForeignKey, Model, CASCADE, DateTimeField,
                              UniqueConstraint, CheckConstraint)


class User(AbstractUser):
    email = models.EmailField(
        'Email',
        max_length=200,
        unique=True, )
    first_name = models.CharField(
        'Имя',
        max_length=150)
    last_name = models.CharField(
        'Фамилия',
        max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.email


class Subscriptions(Model):
    author = ForeignKey(
        verbose_name="Автор рецепта",
        related_name="subscribers",
        to=User,
        on_delete=CASCADE,
    )
    user = ForeignKey(
        verbose_name="Подписчики",
        related_name="subscriptions",
        to=User,
        on_delete=CASCADE,
    )
    date_added = DateTimeField(
        verbose_name="Дата создания подписки",
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = (
            UniqueConstraint(
                fields=("author", "user"),
                name="\nRepeat subscription\n",
            ),
            CheckConstraint(
                check=~Q(author=F("user")), name="\nNo self sibscription\n"
            ),
        )

    def __str__(self) -> str:
        return f"{self.user.username} -> {self.author.username}"
