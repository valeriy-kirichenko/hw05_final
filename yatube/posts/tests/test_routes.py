from django.test import TestCase
from django.urls import reverse


class PostsURLTests(TestCase):
    def test_post_routes(self):
        """Расчет маршрута дает ожидаемый URL."""
        USERNAME = 'author'
        GROUP_SLUG = 'test-slug'
        POST_ID = 1
        cases = [
            ['posts:index', None, '/'],
            ['posts:group_posts', [GROUP_SLUG], f'/group/{GROUP_SLUG}/'],
            ['posts:profile', [USERNAME], f'/profile/{USERNAME}/'],
            ['posts:post_detail', [POST_ID], f'/posts/{POST_ID}/'],
            ['posts:post_edit', [POST_ID], f'/posts/{POST_ID}/edit/'],
            ['posts:post_create', None, '/create/'],
            ['posts:follow_index', None, '/follow/'],
            ['posts:profile_follow',
             [USERNAME],
             f'/profile/{USERNAME}/follow/'],
            ['posts:profile_unfollow',
             [USERNAME],
             f'/profile/{USERNAME}/unfollow/'],
        ]
        for name, argument, expected_url in cases:
            with self.subTest(name=name):
                self.assertEqual(reverse(name, args=argument),
                                 expected_url
                                 )
