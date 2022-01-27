import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Post, Group, User, Comment

USERNAME = 'author'
USERNAME_NOT_AUTHOR = 'not author'
POST_CREATE_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
LOGIN_URL = reverse('users:login')
POST_CREATE_REDIRECT = f'{LOGIN_URL}?next={POST_CREATE_URL}'
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
class PostCreateFormTests(TestCase):
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
            slug='test-slug',
            description='test description',
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=BYTE_STRING,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test text',
            group=cls.group,
            image=cls.image
        )
        cls.POST_EDIT_URL = reverse('posts:post_edit',
                                    args=[cls.post.id])
        cls.POST_DETAIL_URL = reverse('posts:post_detail',
                                      args=[cls.post.id])
        cls.COMMENT_URL = reverse('posts:add_comment', args=[cls.post.id])
        cls.POST_EDIT_REDIRECT = f'{LOGIN_URL}?next={cls.POST_EDIT_URL}'

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        posts = set(Post.objects.all())
        image = SimpleUploadedFile(
            name='small.gif',
            content=BYTE_STRING,
            content_type='image/gif'
        )
        form_data = {
            'text': 'test text 2',
            'group': self.group.id,
            'image': image,
        }
        response = self.author.post(
            POST_CREATE_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, PROFILE_URL)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        posts = set(Post.objects.all()) - posts
        self.assertEqual(len(posts), 1)
        post = posts.pop()
        self.assertIsNotNone(post.image)
        self.assertEqual(form_data['text'], post.text)
        self.assertEqual(form_data['group'], post.group_id)
        self.assertEqual(self.user, post.author)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        posts_count = Post.objects.count()
        group = Group.objects.create(
            title='test group 3',
            slug='test-slug-3',
            description='test description 3',
        )
        image = SimpleUploadedFile(
            name='another_small.gif',
            content=BYTE_STRING,
            content_type='image/gif'
        )
        form_data = {
            'text': 'test text 3',
            'group': group.id,
            'image': image
        }
        response = self.author.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        post = response.context['post']
        self.assertRedirects(response, self.POST_DETAIL_URL)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(form_data['text'], post.text)
        self.assertEqual(form_data['group'], post.group_id)
        self.assertIn(image.name, post.image.name)
        self.assertEqual(self.post.author, post.author)

    def test_post_edit_and_create_pages_show_correct_form(self):
        """Шаблоны create_post и post_edit корректно отоброжают поля формы."""
        urls = [self.POST_EDIT_URL, POST_CREATE_URL]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
            'image': forms.ImageField,
        }
        for url in urls:
            response = self.author.get(url)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_post_detail_show_correct_form(self):
        """Шаблон post_detail корректно отоброжает поле формы."""
        response = self.author.get(self.POST_DETAIL_URL)
        self.assertIsInstance(
            response.context.get('form').fields.get('text'),
            forms.fields.CharField
        )

    def test_guest_cant_comment(self):
        """Гость не может оставить комментарий."""
        comments = set(Comment.objects.all())
        self.guest.post(
            self.COMMENT_URL,
            data={'text': 'Test comment'},
        )
        self.assertFalse(set(Comment.objects.all()) - comments)

    def test_comment_on_post_detail_page(self):
        """Комментарий корректно отображается на странице поста."""
        comments_count = Comment.objects.count()
        comments = set(Comment.objects.all())
        form_data = {'text': 'Test comment'}
        response = self.author.post(
            self.COMMENT_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.POST_DETAIL_URL)
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        comments = set(Comment.objects.all()) - comments
        self.assertEqual(len(comments), 1)
        comment = comments.pop()
        self.assertEqual(form_data['text'], comment.text)
        self.assertEqual(self.user, comment.author)
        self.assertEqual(self.post, response.context['post'])

    def test_guest_cant_create_post(self):
        """Гость не может создать пост."""
        posts = set(Post.objects.all())
        response = self.guest.post(
            POST_CREATE_URL,
            data={
                'text': 'test text 2',
                'group': self.group.id,
                'image': self.image
            },
            follow=True
        )
        self.assertRedirects(response, POST_CREATE_REDIRECT)
        self.assertFalse(set(Post.objects.all()) - posts)

    def test_guest_and_not_author_cant_edit_post(self):
        """Гость и не автор не могут редактировать пост."""
        posts_count = Post.objects.count()
        group = Group.objects.create(
            title='test group 4',
            slug='test-slug-4',
            description='test description 4',
        )
        client_redirect = [
            [self.guest, self.POST_EDIT_REDIRECT],
            [self.not_author, self.POST_DETAIL_URL]
        ]
        for client, redirect in client_redirect:
            with self.subTest(url=redirect):
                response = client.post(
                    self.POST_EDIT_URL,
                    data={'text': 'test text 3', 'group': group.id},
                    follow=True
                )
                self.assertRedirects(response, redirect)
                self.assertEqual(Post.objects.count(), posts_count)
                self.assertEqual(
                    Post.objects.get(id=self.post.id).text,
                    self.post.text
                )
                self.assertEqual(
                    Post.objects.get(id=self.post.id).group_id,
                    self.post.group_id
                )
