import shutil
import tempfile

from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from users.models import UserProfile

USERNAME = 'author'
ANOTHER_USERNAME = 'another user'
INDEX_URL = reverse('posts:index')
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
LOGIN_URL = reverse('users:login')
SIGN_UP_URL = reverse('users:signup')
USER_PROFILE_FORM_URL = reverse('users:user_profile_form', args=[USERNAME])
PASSWORD_CHANGE_URL = reverse('users:password_change_form')
PASSWORD_CHANGE_DONE_URL = reverse('users:password_change_done')
PASSWORD_RESET_FORM_URL = reverse('users:password_reset_form')
PASSWORD_RESET_DONE_URL = reverse('users:password_reset_done')
PASSWORD_RESET_CONFIRM_URL = reverse(
    'users:password_reset_confirm', args=['uid64', 'token']
)
PASSWORD_RESET_COMPLETE_URL = reverse('users:password_reset_complete')
LOGOUT_URL = reverse('users:logout')
UNEXISTING_PAGE_URL = '/unexisting_page/'

LOGIN_REDIRECT = f'{LOGIN_URL}?next={INDEX_URL}'
USER_PROFILE_FORM_GUEST_REDIRECT = f'{LOGIN_URL}?next={USER_PROFILE_FORM_URL}'
USER_PROFILE_FORM_NOT_AUTHOR_REDIRECT = (
    f'{USER_PROFILE_FORM_URL}?next={PROFILE_URL}'
)
PASSWORD_CHANGE_REDIRECT = f'{LOGIN_URL}?next={PASSWORD_CHANGE_URL}'
PASSWORD_CHANGE_DONE_REDIRECT = f'{LOGIN_URL}?next={PASSWORD_CHANGE_DONE_URL}'
PASSWORD_RESET_FORM_REDIRECT = f'{LOGIN_URL}?next={PASSWORD_RESET_FORM_URL}'
PASSWORD_RESET_DONE_REDIRECT = f'{LOGIN_URL}?next={PASSWORD_RESET_DONE_URL}'
PASSWORD_RESET_CONFIRM_REDIRECT = (
    f'{LOGIN_URL}?next={PASSWORD_RESET_CONFIRM_URL}'
)
PASSWORD_RESET_COMPLETE_REDIRECT = (
    f'{LOGIN_URL}?next={PASSWORD_RESET_COMPLETE_URL}'
)
LOGOUT_REDIRECT = f'{LOGIN_URL}?next={LOGOUT_URL}'

NOT_FOUND = 404
FORBIDDEN = 403
FOUND = 302
OK = 200

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
BYTE_STRING = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.another_user = User.objects.create_user(
            username=ANOTHER_USERNAME
        )
        cls.guest = Client()
        cls.author = Client()
        cls.another = Client()
        image = SimpleUploadedFile(
            name='small.gif',
            content=BYTE_STRING,
            content_type='image/gif'
        )
        cls.profile = UserProfile.objects.create(
            user=cls.user,
            avatar=image,
        )

    def setUp(self):
        self.author.force_login(self.user)
        self.another.force_login(self.another_user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_urls_get_correct_templates(self):
        """Провряем что URL-адрес использует соответствующий шаблоны."""
        url_client_template = [
            [LOGIN_URL, self.guest, 'users/login.html'],
            [SIGN_UP_URL, self.guest, 'users/signup.html'],
            [USER_PROFILE_FORM_URL,
             self.author,
             'users/user_profile_form.html'],
            [PASSWORD_CHANGE_URL,
             self.author,
             'users/password_change_form.html'],
            [PASSWORD_CHANGE_DONE_URL,
             self.author,
             'users/password_change_done.html'],
            [PASSWORD_RESET_FORM_URL,
             self.author,
             'users/password_reset_form.html'],
            [PASSWORD_RESET_DONE_URL,
             self.author,
             'users/password_reset_done.html'],
            [PASSWORD_RESET_CONFIRM_URL,
             self.author,
             'users/password_reset_confirm.html'],
            [PASSWORD_RESET_COMPLETE_URL,
             self.author,
             'users/password_reset_complete.html'],
            [LOGOUT_URL, self.author, 'users/logged_out.html'],
        ]
        for url, client, template in url_client_template:
            with self.subTest(url=url, template=template):
                self.assertTemplateUsed(client.get(url), template)

    def test_users_pages(self):
        """Проверка доступности адресов."""
        url_client_status_code = [
            [UNEXISTING_PAGE_URL, self.guest, NOT_FOUND],
            [LOGIN_URL, self.guest, OK],
            [LOGIN_URL, self.author, FOUND],
            [SIGN_UP_URL, self.guest, OK],
            [SIGN_UP_URL, self.author, FORBIDDEN],
            [USER_PROFILE_FORM_URL, self.author, OK],
            [USER_PROFILE_FORM_URL, self.another, FOUND],
            [USER_PROFILE_FORM_URL, self.guest, FOUND],
            [PASSWORD_CHANGE_URL, self.author, OK],
            [PASSWORD_CHANGE_URL, self.guest, FOUND],
            [PASSWORD_CHANGE_DONE_URL, self.author, OK],
            [PASSWORD_CHANGE_DONE_URL, self.guest, FOUND],
            [PASSWORD_RESET_FORM_URL, self.author, OK],
            [PASSWORD_RESET_FORM_URL, self.guest, FOUND],
            [PASSWORD_RESET_DONE_URL, self.author, OK],
            [PASSWORD_RESET_DONE_URL, self.guest, FOUND],
            [PASSWORD_RESET_CONFIRM_URL, self.author, OK],
            [PASSWORD_RESET_CONFIRM_URL, self.guest, FOUND],
            [PASSWORD_RESET_COMPLETE_URL, self.author, OK],
            [PASSWORD_RESET_COMPLETE_URL, self.guest, FOUND],
            [LOGOUT_URL, self.guest, FOUND],
            [LOGOUT_URL, self.author, OK],
        ]
        for url, client, status_code in url_client_status_code:
            with self.subTest(url=url, status_code=status_code):
                self.assertEqual(client.get(url).status_code, status_code)

    def test_users_redirect(self):
        """Редирект работает корректно."""
        url_client_redirect = [
            [LOGIN_URL, self.author, INDEX_URL],
            [USER_PROFILE_FORM_URL, self.another, PROFILE_URL],
            [USER_PROFILE_FORM_URL,
             self.guest,
             USER_PROFILE_FORM_GUEST_REDIRECT],
            [PASSWORD_CHANGE_URL, self.guest, PASSWORD_CHANGE_REDIRECT],
            [PASSWORD_CHANGE_DONE_URL,
             self.guest,
             PASSWORD_CHANGE_DONE_REDIRECT],
            [PASSWORD_RESET_FORM_URL,
             self.guest,
             PASSWORD_RESET_FORM_REDIRECT],
            [PASSWORD_RESET_DONE_URL,
             self.guest,
             PASSWORD_RESET_DONE_REDIRECT],
            [PASSWORD_RESET_CONFIRM_URL,
             self.guest,
             PASSWORD_RESET_CONFIRM_REDIRECT],
            [PASSWORD_RESET_COMPLETE_URL,
             self.guest,
             PASSWORD_RESET_COMPLETE_REDIRECT],
            [LOGOUT_URL, self.guest, LOGOUT_REDIRECT],
        ]
        for url, client, redirect in url_client_redirect:
            with self.subTest(url=url, redirect=redirect):
                self.assertRedirects(client.get(url, follow=True), redirect)
