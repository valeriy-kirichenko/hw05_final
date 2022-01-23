from django.test import TestCase, Client
from django.contrib.auth import models, forms as auth_forms
from django.urls import reverse
from django import forms


class UsersViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.authorized_client = Client()

    def setUp(self):
        self.user = models.User.objects.create_user(
            'noname',
            'noname@noname.com',
            'pass1234pass'
        )
        UsersViewsTests.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template_guest(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('users:login'): 'users/login.html',
            reverse('users:signup'): 'users/signup.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertTemplateUsed(
                    UsersViewsTests.guest_client.get(reverse_name),
                    template
                )

    def test_pages_uses_correct_template_authorized(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('users:password_change_form'):
                'users/password_change_form.html',
            reverse('users:password_change_done'):
                'users/password_change_done.html',
            reverse('users:password_reset_form'):
                'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse('users:password_reset_confirm',
                    args=['<uidb64>', '<token>']
                    ): 'users/password_reset_confirm.html',
            reverse('users:password_reset_complete'):
                'users/password_reset_complete.html',
            reverse('users:logout'): 'users/logged_out.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertTemplateUsed(
                    UsersViewsTests.authorized_client.get(reverse_name),
                    template
                )

    def test_users_sign_up_show_correct_context_guest(self):
        """Шаблон sign_up сформирован с правильным контекстом."""
        response = UsersViewsTests.guest_client.get(
            reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': auth_forms.UsernameField,
            'email': forms.fields.EmailField,
            'password1': forms.fields.CharField,
            'password2': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
