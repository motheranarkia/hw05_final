from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group


User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='posts_author',
        )
        cls.group = Group.objects.create(
            title='test_group_title',
            slug='test_group_slug',
            description='Тестовое описание группы',
        )
        cls.posts = [
            Post(
                text=f'Текст №{post_number}',
                author=cls.user,
                group=cls.group,
            )
            for post_number in range(13)
        ]
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_first_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_contains_three_records(self):
        response = (
            self.authorized_client.get(
                reverse('posts:index'),
                {'page': 2}
            )
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_first_page_contains_ten_records(self):
        response = (
            self.authorized_client.get(
                reverse('posts:group_posts', kwargs={'slug':
                        'test_group_slug'})
            )
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_second_page_contains_three_records(self):
        response = (
            self.authorized_client.get(
                reverse('posts:group_posts', kwargs={'slug':
                        'test_group_slug'}),
                {'page': 2},
            )
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_first_page_contains_ten_records(self):
        response = (
            self.authorized_client.get(
                reverse('posts:profile', kwargs={'username':
                        'posts_author'}))
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_second_page_contains_three_records(self):
        response = (
            self.authorized_client.get(
                reverse('posts:profile', kwargs={'username':
                        'posts_author'}),
                {'page': 2},
            )
        )
        self.assertEqual(len(response.context['page_obj']), 3)
