from core.models import CreatedModel

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class Group(models.Model):
    """Модель для группы.

    Attributes:
        title (str): название группы.
        slug (str): уникальное название латиницей.
        description (str): описание.
    """

    title = models.CharField(max_length=200, verbose_name='Название группы')
    slug = models.SlugField(
        unique=True,
        verbose_name='Уникальное название латиницей'
    )
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        """Возвращает строковое представление модели"""

        return self.title


class Post(CreatedModel):
    """Модель для поста.

    Attributes:
        text (str): текст поста.
        author (int): id автора.
        group (int): id группы.
        image (str): картинка.
    """

    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Текст нового поста'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
        help_text='Укажите автора'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        help_text='Изображение которое имеет отношение к посту'
    )

    class Meta(CreatedModel.Meta):
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        """Возвращает строковое представление модели"""

        return (
            f'{self.pk} {self.text[:15]} {self.created} '
            f'{self.author.get_username()} {self.group}'
        )


class Comment(CreatedModel):
    """Модель для комментариев.

    Attributes:
        post (int): id поста.
        author (int): id автора.
        text (str): текст комментария.
    """

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост',
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='comments',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария'
    )

    class Meta(CreatedModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    """Модель для подписок.

    Attributes:
        user (int): id подписчика.
        author (int): id пользователя на которого подписываются.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='following',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def clean(self):
        """Проверка создаваемого объекта.

        Raises:
            ValidationError: ошибка при попытке подписки на самого себя.
        Raises:
            ValidationError: ошибка при попытке подписки на автора более
            одного раза.
        """

        if self.user == self.author:
            raise ValidationError('Вы не можете подписаться на самого себя')
        if self.author.following.count() > 0:
            raise ValidationError(
                'Нельзя подписаться на автора более одного раза'
            )

    def save(self, *args, **kwargs):
        """Вызывает метод full_clean() класса для запуска всех проверок."""

        self.full_clean()
        return super().save(*args, **kwargs)
