from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # неавторизованный клиент
        cls.guest_client = Client()
        # авторизованный клиент
        cls.user = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        # авторизованный клиент автор
        cls.author = User.objects.create_user(username='test_author')
        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.author)
        # авторизованный клиент не-автор
        cls.non_author = User.objects.create_user(username='test_non_author')
        cls.authorized_non_author_client = Client()
        cls.authorized_non_author_client.force_login(cls.non_author)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts',
                    kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.author}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}): 'posts/create_post.html',
            reverse('posts:create_post'): 'posts/create_post.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = PostURLTests.authorized_author.get(
                    adress, follow=True
                )
                self.assertTemplateUsed(response, template)

    def test_urls_guest(self):
        """Страницы, доступные для неавторизованного клиента"""
        urls = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse('posts:group_posts',
                    kwargs={'slug': 'test_slug'}): HTTPStatus.OK,
            reverse('posts:profile',
                    kwargs={'username': self.author}): HTTPStatus.OK,
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}): HTTPStatus.OK,
            reverse('posts:create_post'): HTTPStatus.FOUND,
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}): HTTPStatus.FOUND,
        }
        for adress, expected in urls.items():
            with self.subTest(adress=adress):
                response = PostURLTests.guest_client.get(adress)
                self.assertEqual(response.status_code, expected)

    def test_urls(self):
        """Страницы, доступные для авторизованного клиента"""
        urls = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse('posts:group_posts',
                    kwargs={'slug': 'test_slug'}): HTTPStatus.OK,
            reverse('posts:profile',
                    kwargs={'username': self.author}): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}): HTTPStatus.OK,
            reverse('posts:create_post'): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}): HTTPStatus.OK,
        }
        for adress, expected in urls.items():
            with self.subTest(adress=adress):
                response = PostURLTests.authorized_author.get(adress)
                self.assertEqual(response.status_code, expected)

    def test_page_404(self):
        """Несуществующая страница отвечает 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
