from django.test import Client, TestCase


class ViewTestClass(TestCase):
    def test_error_page(self):
        client = Client()
        self.assertTemplateUsed(
            client.get('/unexisting_page/'),
            'core/404.html'
        )
