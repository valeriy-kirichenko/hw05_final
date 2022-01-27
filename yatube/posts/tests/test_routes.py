from django.test import TestCase
from django.urls import reverse

from posts import views


class PostsURLTests(TestCase):
    def test_post_routes(self):
        """Расчет маршрута дает ожидаемый URL."""
        USERNAME = 'author'
        GROUP_SLUG = 'test-slug'
        POST_ID = 1
        cases = [
            [views.index.__name__, None, '/'],
            [views.group_posts.__name__,
             [GROUP_SLUG],
             f'/group/{GROUP_SLUG}/'],
            [views.profile.__name__, [USERNAME], f'/profile/{USERNAME}/'],
            [views.post_detail.__name__, [POST_ID], f'/posts/{POST_ID}/'],
            [views.post_edit.__name__, [POST_ID], f'/posts/{POST_ID}/edit/'],
            [views.post_create.__name__, None, '/create/'],
            [views.follow_index.__name__, None, '/follow/'],
            [views.profile_follow.__name__,
             [USERNAME],
             f'/profile/{USERNAME}/follow/'],
            [views.profile_unfollow.__name__,
             [USERNAME],
             f'/profile/{USERNAME}/unfollow/'],
        ]
        for name, argument, expected_url in cases:
            with self.subTest(name=name):
                self.assertEqual(reverse(f'posts:{name}', args=argument),
                                 expected_url
                                 )
