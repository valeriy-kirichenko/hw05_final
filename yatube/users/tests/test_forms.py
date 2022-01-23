from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class UsersSignupFormTests(TestCase):
    def setUp(self):
        self.guest = Client()

    def test_create_user(self):
        """Валидная форма создает нового пользователя."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'test_first_name',
            'last_name': 'test_last_name',
            'username': 'test_username',
            'email': 'test@email.ru',
            'password1': 'f365!F123',
            'password2': 'f365!F123'
        }
        """ response = UsersSignupFormTests.guest.get(reverse('users:signup'))
        print(response.context[0]) """
        response = self.guest.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                username='test_username'
            ).exists()
        )
