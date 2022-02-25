import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from ..models import Group, Post, Comment
from ..forms import PostForm

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_author')
        cls.non_author = User.objects.create_user(username='test_non_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Описание группы',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
            group=cls.group,
        )
        cls.form = PostForm()
        cls.comment = Comment.objects.create(
            text='Комментарий', author=cls.author, post=cls.post
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        self.authorized_non_author = Client()
        self.authorized_non_author.force_login(self.non_author)

    def test_create_post(self):
        """при отправке валидной формы создаётся новая запись."""
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B')
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif')
        form_data = {
            'text': 'Тестовый текст',
            'image': uploaded,
        }
        posts_count = Post.objects.count()
        self.authorized_author.post(
            reverse('posts:create_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        last_object = Post.objects.last()
        self.assertEqual(last_object.group.id, self.group.id)
        self.assertEqual(last_object.text, self.post.text)
        self.assertEqual(last_object.image, self.post.image)

    def test_edit_post(self):
        """при отправке валидной формы происходит изменение поста."""
        form_data = {
            'text': 'Новый пост',
            'group': self.group.id,
        }
        self.authorized_author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        changed_post = Post.objects.get(id=self.post.id)
        self.assertEqual(changed_post.text, form_data['text'])
        self.assertEqual(changed_post.group.id, form_data['group'])

    def test_guest_can_not_create_new_post(self):
        """неавторизованный клиент перенаправляется на страницу
        авторизации"""
        posts_count = Post.objects.count()
        response = self.guest_client.post(
            reverse(
                'posts:create_post'), follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(posts_count, Post.objects.count())

    def test_user_can_not_edit_post(self):
        """пользователь не может редактировать чужой пост"""
        form_data = {
            'text': 'Измененный тестовый пост',
        }
        response = self.authorized_non_author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.non_author})
        )
        self.assertEqual(
            Post.objects.get(id=self.post.id).text,
            PostFormFormTests.post.text
        )

    def test_create_comment(self):
        """Авторизованный пользователь может комментировать"""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Новый комментарий',
            'author': self.post.author,
            'post_id': self.post.id
        }
        response = self.authorized_author.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})
        )
        last_comment = Comment.objects.order_by("-id").first()
        self.assertEqual(form_data['text'], last_comment.text)
        self.assertEqual(form_data['author'], self.post.author)
        self.assertEqual(form_data['post_id'], self.post.id)
        self.assertEqual(Comment.objects.count(), comment_count + 1)

    def test_guest_can_not_add_comment(self):
        """А неавторизованный - нет"""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Новый комментарий',
        }
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count)
