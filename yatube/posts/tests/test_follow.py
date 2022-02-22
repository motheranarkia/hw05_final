from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Follow, Post

User = get_user_model()


class FollowPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower_user = User.objects.create_user(username='follower')
        cls.unfollower_user = User.objects.create_user(username='non_follower')
        cls.author = User.objects.create_user(username='author')
        cls.follow = Follow.objects.create(
            user=cls.follower_user,
            author=cls.author,
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
        )

    def setUp(self):
        self.follower_client = Client()
        self.follower_client.force_login(self.follower_user)
        self.unfollower_client = Client()
        self.unfollower_client.force_login(self.unfollower_user)

    def test_auth_user_follow_or_unfollow(self):
        """Авторизованный пользователь может подписываться на других
        пользователей и удалять их из подписок."""
        follow_count = Follow.objects.count()
        self.unfollower_client.get(
            reverse('posts:profile', kwargs={'username': self.author}))
        self.follow = Follow.objects.create(
            user=self.unfollower_user,
            author=self.author,
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.follow_del = Follow.objects.filter(
            user=self.unfollower_user,
            author=self.author,
        ).delete()
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_follow_post(self):
        """Проверка появления записей в ленте у подписчиков,
        и отсутствия ее у неподписанных"""
        Follow.objects.create(author=self.author, user=self.follower_user)
        response = self.follower_client.get('/follow/')
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Тестовый текст')
        Post.objects.create(text='Тестовый текст для неподписанных',
                            author=self.author)
        post = Post.objects.get(text='Тестовый текст для неподписанных')
        response = self.unfollower_client.get('/follow/')
        self.assertNotContains(response, post)
