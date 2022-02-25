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
        follows_count = Follow.objects.count()
        self.assertFalse(Follow.objects.filter(
            user=self.unfollower_user,
            author=self.author).exists()
        )
        self.unfollower_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.author})
        )
        self.assertEqual(Follow.objects.count(), follows_count + 1)
        self.assertTrue(Follow.objects.filter(
            user=self.unfollower_user,
            author=self.author,
        ).exists())

    def test_user_unfollow(self):
        """Юзер может отписываться"""
        Follow.objects.create(author=self.author, user=self.unfollower_user)
        follows_before = Follow.objects.count()
        self.unfollower_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.author})
        )
        self.assertEqual(Follow.objects.count(), follows_before - 1)

    def test_follow_post(self):
        """Новый пост появляется в ленте подписчика"""
        Follow.objects.create(author=self.author, user=self.unfollower_user)
        response = self.follower_client.get(reverse('posts:follow_index'))
        count_posts = len(response.context['page_obj'])
        Post.objects.create(author=self.author, text='Тестовый текст')
        response = self.follower_client.get(reverse('posts:follow_index'))
        new_count_posts = len(response.context['page_obj'])
        self.assertEqual(count_posts + 1, new_count_posts)

    def test_posts_new_post_not_add_to_not_follower(self):
        """Новый пост не появляется в ленте не_подписчика."""
        response = self.unfollower_client.get(reverse('posts:follow_index'))
        count_posts = len(response.context['page_obj'])
        Post.objects.create(author=self.author, text='Тестовый текст')
        response = self.unfollower_client.get(reverse('posts:follow_index'))
        new_count_posts = len(response.context['page_obj'])
        self.assertEqual(count_posts, new_count_posts)
