from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, User

USERNAME = 'author'
ANOTHER_USERNAME = 'another user'
GROUP_SLUG = 'test-slug'
LOGIN_URL = reverse('users:login')
INDEX_URL = reverse('posts:index')
GROUP_POSTS_URL = reverse('posts:group_posts', args=[GROUP_SLUG])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
POST_CREATE_URL = reverse('posts:post_create')
FOLLOW_INDEX_URL = reverse('posts:follow_index')
FOLLOW_TO_AUTHOR_URL = reverse('posts:profile_follow', args=[USERNAME])
UNFOLLOW_TO_AUTHOR_URL = reverse('posts:profile_unfollow', args=[USERNAME])
UNEXISTING_PAGE_URL = '/unexisting_page/'
POST_CREATE_REDIRECT = f'{LOGIN_URL}?next={POST_CREATE_URL}'
FOLLOW_INDEX_REDIRECT = f'{LOGIN_URL}?next={FOLLOW_INDEX_URL}'
FOLLOW_TO_AUTHOR_REDIRECT = f'{LOGIN_URL}?next={FOLLOW_TO_AUTHOR_URL}'
UNFOLLOW_TO_AUTHOR_REDIRECT = f'{LOGIN_URL}?next={UNFOLLOW_TO_AUTHOR_URL}'
NOT_FOUND = 404
FOUND = 302
OK = 200


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.another_user = User.objects.create_user(
            username=ANOTHER_USERNAME
        )
        cls.group = Group.objects.create(
            title='test group',
            slug=GROUP_SLUG,
            description='test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test text',
            group=cls.group,
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])
        cls.POST_EDIT_REDIRECT = f'{LOGIN_URL}?next={cls.POST_EDIT_URL}'
        cls.COMMENT_URL = reverse('posts:add_comment', args=[cls.post.id])
        cls.POST_COMMENT_REDIRECT = f'{LOGIN_URL}?next={cls.COMMENT_URL}'

    def setUp(self):
        self.guest = Client()
        self.author = Client()
        self.another = Client()
        self.author.force_login(self.user)
        self.another.force_login(self.another_user)

    def test_urls_get_correct_templates(self):
        """Провряем что URL-адреса используют соответствующие шаблоны."""
        url_client_template = [
            [INDEX_URL, self.guest, 'posts/index.html'],
            [GROUP_POSTS_URL, self.guest, 'posts/group_list.html'],
            [PROFILE_URL, self.guest, 'posts/profile.html'],
            [self.POST_DETAIL_URL, self.guest, 'posts/post_detail.html'],
            [POST_CREATE_URL, self.author, 'posts/create_post.html'],
            [self.POST_EDIT_URL, self.author, 'posts/create_post.html'],
            [FOLLOW_INDEX_URL, self.author, 'posts/follow.html'],
        ]
        for url, client, template in url_client_template:
            with self.subTest(url=url, client=client, template=template):
                self.assertTemplateUsed(client.get(url), template)

    def test_urls_exists_at_desired_location(self):
        """Проверка доступности адресов."""
        url_client_status_code = [
            [INDEX_URL, self.guest, OK],
            [GROUP_POSTS_URL, self.guest, OK],
            [PROFILE_URL, self.guest, OK],
            [self.POST_DETAIL_URL, self.guest, OK],
            [POST_CREATE_URL, self.author, OK],
            [self.POST_EDIT_URL, self.author, OK],
            [UNEXISTING_PAGE_URL, self.guest, NOT_FOUND],
            [self.POST_EDIT_URL, self.guest, FOUND],
            [POST_CREATE_URL, self.guest, FOUND],
            [self.POST_EDIT_URL, self.another, FOUND],
            [self.COMMENT_URL, self.guest, FOUND],
            [self.COMMENT_URL, self.author, FOUND],
            [FOLLOW_INDEX_URL, self.author, OK],
            [FOLLOW_TO_AUTHOR_URL, self.another, FOUND],
            [UNFOLLOW_TO_AUTHOR_URL, self.another, FOUND],
            [UNFOLLOW_TO_AUTHOR_URL, self.author, NOT_FOUND],
        ]
        for url, client, status_code in url_client_status_code:
            with self.subTest(url=url, status_code=status_code):
                self.assertEqual(client.get(url).status_code, status_code)

    def test_redirect(self):
        """Редирект работает корректно."""
        url_client_redirect = [
            [POST_CREATE_URL, self.guest, POST_CREATE_REDIRECT],
            [self.POST_EDIT_URL, self.guest, self.POST_EDIT_REDIRECT],
            [self.POST_EDIT_URL, self.another, self.POST_DETAIL_URL],
            [self.COMMENT_URL, self.guest, self.POST_COMMENT_REDIRECT],
            [FOLLOW_INDEX_URL, self.guest, FOLLOW_INDEX_REDIRECT],
            [FOLLOW_TO_AUTHOR_URL, self.guest, FOLLOW_TO_AUTHOR_REDIRECT],
            [UNFOLLOW_TO_AUTHOR_URL, self.guest, UNFOLLOW_TO_AUTHOR_REDIRECT],
            [FOLLOW_TO_AUTHOR_URL, self.author, PROFILE_URL],
        ]
        for url, client, redirect in url_client_redirect:
            with self.subTest(url=url, redirect=redirect):
                self.assertRedirects(client.get(url, follow=True), redirect)
