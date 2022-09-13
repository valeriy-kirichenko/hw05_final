from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Модель для профиля пользователя.

    Attributes:
        user (int): id пользователя.
        avatar (str): аватар.
        about (str): о себе.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='userprofile',
        null=True,
        blank=True
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='avatars',
        help_text='Выберите фото которое вам по душе',
        null=True,
        blank=True
    )
    about = models.CharField(
        max_length=300,
        verbose_name='О себе',
        help_text='Напишите немного о себе (не более 300 символов)',
        blank=True,
        default='Автор еще не заполнил этот раздел',
    )

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        """Возвращает строковое представление модели"""

        return self.user.username

    def get_avatar(self):
        """Проверяет наличие аватара.

        Returns:
            str: url аватара по умолчанию если пользоваетль не загружал
            собственный.
        Returns:
            str: url аватара пользователя.
        """

        if not self.avatar:
            return '/static/img/Missing_avatar.svg'
        return self.avatar.url
