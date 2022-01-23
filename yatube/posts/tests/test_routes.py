from django.test import TestCase
from django.urls import reverse


class PostsURLTests(TestCase):
    def test_post_routes(self):
        """Расчет маршрута дает ожидаемый URL."""
        USERNAME = 'author'
        GROUP_SLUG = 'test-slug'
        POST_ID = 1
        cases = [
            ['index', None, '/'],
            ['group_posts', [GROUP_SLUG], f'/group/{GROUP_SLUG}/'],
            ['profile', [USERNAME], f'/profile/{USERNAME}/'],
            ['post_detail', [POST_ID], f'/posts/{POST_ID}/'],
            ['post_edit', [POST_ID], f'/posts/{POST_ID}/edit/'],
            ['post_create', None, '/create/'],
            ['follow_index', None, '/follow/'],
            ['profile_follow', [USERNAME], f'/profile/{USERNAME}/follow/'],
            ['profile_unfollow', [USERNAME], f'/profile/{USERNAME}/unfollow/'],
        ]
        for name, argument, expected_url in cases:
            with self.subTest(name=name):
                self.assertEqual(reverse(f'posts:{name}', args=argument),
                                 expected_url
                                 )
