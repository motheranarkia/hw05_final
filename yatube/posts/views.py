from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings

from posts.models import Post, Group, User, Comment, Follow
from posts.forms import PostForm, CommentForm


def pagination(posts,
               page_number: int,
               paginator_count_of_posts: int = settings.POST_COUNT
               ) -> int:
    paginator = Paginator(posts, paginator_count_of_posts)
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    posts = Post.objects.all().order_by('-pub_date')
    page_number = request.GET.get('page')
    page_obj = pagination(posts, page_number)

    context = {
        'page_obj': page_obj,
        'posts': posts,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_number = request.GET.get('page')
    page_obj = pagination(posts, page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    posts_counter = post_list.count()
    page_number = request.GET.get('page')
    page_obj = pagination(post_list, page_number)
    context = {
        'author': author,
        'page_obj': page_obj,
        'posts_counter': posts_counter,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    username_obj = User.objects.get(username=post.author)
    posts_counter = username_obj.posts.count()
    template = 'posts/post_detail.html'
    form = CommentForm()
    comments = Comment.objects.filter(post_id=post_id)
    context = {
        'post': post,
        'posts_counter': posts_counter,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required()
def create_post(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', username=request.user.username)
    context = {
        'form': form,
        'id_edit': False,
    }
    return render(request, template, context)


@login_required()
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:profile', username=request.user.username)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, id=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user).all()
    page_obj = pagination(post_list, request)
    context = {'page_obj': page_obj}
    template = 'posts/follow.html'
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора"""
    user = request.user
    author = get_object_or_404(User, username=username)
    if user != author:
        Follow.objects.get_or_create(
            user=user,
            author=author,
        )
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    template = 'posts:profile'
    get_object_or_404(
        Follow, user=request.user, author__username=username
    ).delete()
    return redirect(template, username=username)
