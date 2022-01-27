from django.test import TestCase, Client
from django.urls import reverse

ABOUT_AUTHOR_URL = reverse('about:author')
ABOUT_TECH_URL = reverse('about:tech')
OK = 200


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest = Client()

    def test_urls_get_correct_templates(self):
        """Провряем что URL-адреса используют соответствующие шаблоны."""
        templates_url_names = {
            ABOUT_AUTHOR_URL: 'about/author.html',
            ABOUT_TECH_URL: 'about/tech.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.guest.get(url),
                    template
                )

    def test_about_pages(self):
        """Проверка доступности адресов."""
        url_list = [ABOUT_AUTHOR_URL, ABOUT_TECH_URL]
        for url in url_list:
            with self.subTest(url=url):
                self.assertEqual(self.guest.get(url).status_code, OK)
