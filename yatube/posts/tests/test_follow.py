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

    def test_user_follow(self):
        """Юзер может подписываться"""
        self.unfollower_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.author}))
        self.assertTrue(Follow.objects.filter(
            user=self.unfollower_user,
            author=self.author,
        ).exists())

    def test_user_unfollow(self):
        """Юзер может отписываться"""
        self.unfollower_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.author}))
        self.assertFalse(Follow.objects.filter(
            user=self.unfollower_user,
            author=self.author,
        ).exists())

    def test_follow_post(self):
        """Проверка появления записей в ленте у подписчиков,
        и отсутствия ее у неподписанных"""
        Follow.objects.create(author=self.author, user=self.follower_user)
        response = self.follower_client.get(reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Тестовый текст')
        post = Post.objects.create(
            text='Тестовый текст для неподписанных',
            author=self.author
        )
        response = self.unfollower_client.get(reverse('posts:follow_index'))
        self.assertNotIn(post, response.context['page_obj'])
