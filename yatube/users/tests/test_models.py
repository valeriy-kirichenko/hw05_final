from django.test import TestCase

from ..models import UserProfile, User


class UserProfileModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.profile = UserProfile.objects.create(
            user=cls.user,
            about='test description',
        )

    def test_user_profile_model_have_correct_object_names(self):
        """Проверяем, что у модели корректно работает __str__."""
        self.assertEqual(self.profile.user.get_username(), str(self.profile))

    def test_user_profile_verbose_names(self):
        """Проверяем verbose_name у полей."""
        field_verboses = {
            'user': 'Пользователь',
            'avatar': 'Аватар',
            'about': 'О себе'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    UserProfile._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_user_profile_help_text(self):
        """Проверяем help_text у полей."""
        field_verboses = {
            'avatar': 'Выберите фото которое вам по душе',
            'about': 'Напишите немного о себе (не более 300 символов)'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    UserProfile._meta.get_field(field).help_text,
                    expected_value
                )
