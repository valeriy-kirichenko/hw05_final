from django.test import TestCase, Client
from django.contrib.auth.models import User

from http import HTTPStatus


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.authorized_client = Client()

    def setUp(self):
        self.user = User.objects.create_user(
            'noname',
            'noname@noname.com',
            'pass1234pass'
        )
        UsersURLTests.authorized_client.force_login(self.user)

    def test_urls_get_correct_templates_for_guest(self):
        """Провряем что URL-адрес использует соответствующий шаблоны."""
        templates_url_names = {
            '/auth/login/': 'users/login.html',
            '/auth/signup/': 'users/signup.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                self.assertTemplateUsed(
                    UsersURLTests.guest_client.get(address),
                    template
                )

    def test_urls_get_correct_templates_for_authorized(self):
        """Провряем что URL-адреса используют соответствующие шаблоны."""
        templates_url_names = {
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset_form/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/<uid64>/<token>/':
                'users/password_reset_confirm.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/logout/': 'users/logged_out.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                self.assertTemplateUsed(
                    UsersURLTests.authorized_client.get(address),
                    template
                )

    def test_users_pages_for_guest(self):
        """Проверка доступности адресов."""
        url_list = [
            '/auth/login/',
            '/auth/signup/'
        ]
        for url in url_list:
            with self.subTest(url=url):
                self.assertEqual(
                    self.guest_client.get(url).status_code,
                    HTTPStatus.OK
                )

    def test_users_pages_for_authorized(self):
        """Проверка доступности адресов."""
        url_list = [
            '/auth/password_reset_form/',
            '/auth/password_reset/done/',
            '/auth/reset/<uid64>/<token>/',
            '/auth/reset/done/',
            '/auth/password_change/',
            '/auth/password_change/done/',
            '/auth/logout/'
        ]
        for url in url_list:
            with self.subTest(url=url):
                self.assertEqual(
                    self.authorized_client.get(url).status_code,
                    HTTPStatus.OK
                )
