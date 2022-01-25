import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Follow, Post, Group, User
from yatube.settings import POSTS_PER_PAGE

USERNAME = 'author'
USERNAME_NOT_AUTHOR = 'not author'
GROUP_SLUG = 'test-slug'
GROUP_SLUG_2 = 'test-slug-2'
LOGIN_URL = reverse('users:login')
INDEX_URL = reverse('posts:index')
GROUP_POSTS_URL = reverse('posts:group_posts', args=[GROUP_SLUG])
GROUP_POSTS_2_URL = reverse('posts:group_posts', args=[GROUP_SLUG_2])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
POST_CREATE_URL = reverse('posts:post_create')
FOLLOW_TO_AUTHOR_URL = reverse('posts:profile_follow', args=[USERNAME])
UNFOLLOW_TO_AUTHOR_URL = reverse('posts:profile_unfollow', args=[USERNAME])
FOLLOW_INDEX_URL = reverse('posts:follow_index')
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
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user_not_author = User.objects.create_user(
            username=USERNAME_NOT_AUTHOR
        )
        cls.guest = Client()
        cls.author = Client()
        cls.not_author = Client()
        cls.author.force_login(cls.user)
        cls.not_author.force_login(cls.user_not_author)
        cls.group = Group.objects.create(
            title='test group',
            slug=GROUP_SLUG,
            description='test description',
        )
        image = SimpleUploadedFile(
            name='small.gif',
            content=BYTE_STRING,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test text',
            group=cls.group,
            image=image
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_show_correct_context(self):
        """Шаблоны сформированы с правильными контекстами
        и созданный пост корректно отображатся на страницах."""
        self.not_author.get(FOLLOW_TO_AUTHOR_URL)
        url_key = [
            [INDEX_URL, self.guest, 'page_obj'],
            [GROUP_POSTS_URL, self.guest, 'page_obj'],
            [PROFILE_URL, self.guest, 'page_obj'],
            [self.POST_DETAIL_URL, self.guest, 'post'],
            [FOLLOW_INDEX_URL, self.not_author, 'page_obj'],
        ]
        for url, client, key in url_key:
            with self.subTest(url=url):
                post = client.get(url).context[key]
                if url != self.POST_DETAIL_URL:
                    self.assertEqual(len(post), 1)
                    post = post[0]
                self.assertEqual(post, self.post)
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.group, self.post.group)
                self.assertEqual(post.image, self.post.image)

    def test_post_author_on_profile_page(self):
        """Автор отображается на странице профиля."""
        response = self.guest.get(PROFILE_URL)
        self.assertEqual(response.context['author'], self.post.author)

    def test_post_group_on_group_posts_page(self):
        """Группа отображается на странице постов группы."""
        response = self.guest.get(GROUP_POSTS_URL).context['group']
        self.assertEqual(response, self.post.group)
        self.assertEqual(response.slug, self.group.slug)
        self.assertEqual(response.description, self.group.description)

    def test_post_not_on_another_group_posts_page(self):
        """Пост не отображается на странице не своей группы."""
        Group.objects.create(
            title='test group 2',
            slug=GROUP_SLUG_2,
            description='test description',
        )
        response = self.guest.get(GROUP_POSTS_2_URL)
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_pages_contains_correct_number_of_posts(self):
        """Paginator работает корректно на первой и второй странице."""
        Post.objects.bulk_create(
            Post(
                author=self.user,
                text=f'Test text {i}',
                group=self.group
            ) for i in range(POSTS_PER_PAGE + 4)
        )
        posts_count = Post.objects.count()
        second_page_posts_count = posts_count - POSTS_PER_PAGE
        url_posts_on_page = [
            [INDEX_URL, POSTS_PER_PAGE],
            [GROUP_POSTS_URL, POSTS_PER_PAGE],
            [PROFILE_URL, POSTS_PER_PAGE],
            [INDEX_URL + '?page=2', second_page_posts_count],
            [GROUP_POSTS_URL + '?page=2', second_page_posts_count],
            [PROFILE_URL + '?page=2', second_page_posts_count],
        ]
        for url, posts_on_page in url_posts_on_page:
            with self.subTest(url=url):
                response = self.guest.get(url)
                self.assertEqual(
                    len(response.context['page_obj']),
                    posts_on_page
                )

    def test_cache_index_page(self):
        """Проверка кеширования главной страницы."""
        cached = self.guest.get(INDEX_URL).content
        Post.objects.all().delete()
        self.assertEqual(self.guest.get(INDEX_URL).content, cached)
        cache.clear()
        self.assertNotEqual(self.guest.get(INDEX_URL).content, cached)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create_user(username='follower')
        cls.not_follower = User.objects.create_user(username='not follower')
        cls.author_user = User.objects.create_user(username=USERNAME)
        cls.author = Client()
        cls.user_1 = Client()
        cls.user_2 = Client()
        cls.author.force_login(cls.author_user)
        cls.user_1.force_login(cls.follower)
        cls.user_2.force_login(cls.not_follower)
        cls.post = Post.objects.create(
            author=cls.author_user,
            text='test text',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_authorized_can_follow(self):
        """Авторизованный пользователь может
        подписываться на других пользователей."""
        self.user_1.get(FOLLOW_TO_AUTHOR_URL)
        self.assertTrue(Follow.objects.filter(
            user=self.follower.id,
            author=self.author_user.id).exists()
        )
        self.assertEqual(
            self.user_1.get(FOLLOW_INDEX_URL).context['page_obj'][0].author,
            self.post.author
        )

    def test_authorized_can_unfollow(self):
        """Авторизованный пользователь может отказаться от подписки."""
        self.user_1.get(FOLLOW_TO_AUTHOR_URL)
        follow_count = len(
            self.user_1.get(FOLLOW_INDEX_URL).context['page_obj']
        )
        self.user_1.get(UNFOLLOW_TO_AUTHOR_URL)
        self.assertFalse(Follow.objects.filter(
            user=self.follower.id,
            author=self.author_user.id).exists()
        )
        self.assertNotEqual(
            follow_count,
            len(self.user_1.get(FOLLOW_INDEX_URL).context['page_obj'])
        )

    def test_follow_index_page_show_new_author_post(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан."""
        self.user_1.get(FOLLOW_TO_AUTHOR_URL)
        post_2 = Post.objects.create(
            author=self.author_user,
            text='test text 2',
        )
        client_assert = [
            [self.user_1, self.assertIn],
            [self.user_2, self.assertNotIn],
        ]
        for client, asert in client_assert:
            asert(post_2, client.get(FOLLOW_INDEX_URL).context['page_obj'])
