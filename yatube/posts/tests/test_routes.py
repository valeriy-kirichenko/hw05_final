from django.test import TestCase
from django.urls import reverse, resolve


class PostsURLTests(TestCase):
    def test_post_routes(self):
        """Расчет маршрута дает ожидаемый URL."""
        USERNAME = 'author'
        GROUP_SLUG = 'test-slug'
        POST_ID = 1
        cases = [
            [None, '/'],
            [[GROUP_SLUG], f'/group/{GROUP_SLUG}/'],
            [[USERNAME], f'/profile/{USERNAME}/'],
            [[POST_ID], f'/posts/{POST_ID}/'],
            [[POST_ID], f'/posts/{POST_ID}/edit/'],
            [None, '/create/'],
            [None, '/follow/'],
            [[USERNAME], f'/profile/{USERNAME}/follow/'],
            [[USERNAME], f'/profile/{USERNAME}/unfollow/'],
        ]
        for argument, expected_url in cases:
            with self.subTest(url=expected_url):
                self.assertEqual(
                    reverse(resolve(expected_url).view_name, args=argument),
                    expected_url
                )
