from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, User
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
BYTE_STRING = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
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

    def setUp(self):
        self.guest = Client()
        self.author = Client()
        self.author.force_login(self.user)

    def test_pages_show_correct_context(self):
        """Шаблоны сформированы с правильными контекстами
        и созданный пост корректно отображатся на страницах."""
        url_key = [
            [INDEX_URL, 'page_obj'],
            [GROUP_POSTS_URL, 'page_obj'],
            [PROFILE_URL, 'page_obj'],
            [self.POST_DETAIL_URL, 'post'],
        ]
        for url, key in url_key:
            with self.subTest(url=url):
                post = self.guest.get(url).context[key]
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
        post = Post.objects.create(author=self.user, text='test text')
        cached = self.guest.get(INDEX_URL).content
        post.delete()
        self.assertEqual(self.guest.get(INDEX_URL).content, cached)
        cache.clear()
        self.assertNotEqual(self.guest.get(INDEX_URL).content, cached)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create_user(username='follower')
        cls.not_follower = User.objects.create_user(username='not follower')
        cls.author_user = User.objects.create_user(username=USERNAME)
        cls.post = Post.objects.create(
            author=cls.author_user,
            text='test text',
        )

    def setUp(self):
        self.author = Client()
        self.user_1 = Client()
        self.user_2 = Client()
        self.author.force_login(self.author_user)
        self.user_1.force_login(self.follower)
        self.user_2.force_login(self.not_follower)

    def test_authorized_can_follow_and_unfollow(self):
        """Авторизованный пользователь может подписываться
        на других пользователей и удалять их из подписок."""
        self.user_1.get(FOLLOW_TO_AUTHOR_URL)
        self.assertEqual(
            len(Post.objects.filter(author=self.post.author)),
            len(self.user_1.get(FOLLOW_INDEX_URL).context['page_obj'])
        )
        self.assertEqual(
            self.user_1.get(FOLLOW_INDEX_URL).context['page_obj'][0].author,
            self.post.author
        )
        self.user_1.get(UNFOLLOW_TO_AUTHOR_URL)
        self.assertEqual(
            len(self.user_1.get(FOLLOW_INDEX_URL).context['page_obj']),
            0
        )

    def test_follow_index_page_show_new_author_post(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан."""
        self.user_1.get(FOLLOW_TO_AUTHOR_URL)
        posts_count = len(
            self.user_1.get(FOLLOW_INDEX_URL).context['page_obj']
        )
        post_2 = Post.objects.create(
            author=self.author_user,
            text='test text 2',
        )
        self.assertEqual(
            posts_count + 1,
            len(self.user_1.get(FOLLOW_INDEX_URL).context['page_obj'])
        )
        self.assertEqual(
            post_2.text,
            self.user_1.get(FOLLOW_INDEX_URL).context['page_obj'][0].text
        )
        self.assertEqual(
            0,
            len(self.user_2.get(FOLLOW_INDEX_URL).context['page_obj'])
        )
