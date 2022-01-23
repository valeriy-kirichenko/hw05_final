from django.test import TestCase, Client
from django.urls import reverse

from http import HTTPStatus


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest = Client()

    def test_urls_get_correct_templates(self):
        """Провряем что URL-адреса используют соответствующие шаблоны."""
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                self.assertTemplateUsed(
                    self.guest.get(address),
                    template
                )

    def test_about_pages(self):
        """Проверка доступности адресов."""
        url_list = ['/about/author/', '/about/tech/']
        for url in url_list:
            with self.subTest(url=url):
                self.assertEqual(
                    self.guest.get(url).status_code,
                    HTTPStatus.OK
                )


class AboutViewsTests(TestCase):
    def setUp(self):
        self.guest = Client()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertTemplateUsed(
                    self.guest.get(reverse_name),
                    template
                )
