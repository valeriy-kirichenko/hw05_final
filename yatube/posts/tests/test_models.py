from django.test import TestCase

from ..models import Follow, Comment, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='test group',
            slug='test-slig',
            description='test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test text',
            group=cls.group,
        )

    def test_post_model_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        expected_message = (
            f'{self.post.pk} {self.post.text[:15]} {self.post.created} '
            f'{self.post.author.get_username()} {self.post.group}'
        )
        self.assertEqual(expected_message, str(self.post))

    def test_post_verbose_names(self):
        """Проверяем verbose_name у полей."""
        field_verboses = {
            'text': 'Текст поста',
            'created': 'Дата создания',
            'author': 'Автор'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_group_verbose_names(self):
        """Проверяем verbose_name у полей."""
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Уникальное название латиницей',
            'description': 'Описание'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Group._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_comment_verbose_names(self):
        """Проверяем verbose_name у полей."""
        field_verboses = {
            'post': 'Пост',
            'author': 'Автор',
            'text': 'Текст комментария'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Comment._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_follow_verbose_names(self):
        """Проверяем verbose_name у полей."""
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Follow._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_text(self):
        """Проверяем help_text."""
        field_verboses = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
            'author': 'Укажите автора',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).help_text,
                    expected_value
                )
