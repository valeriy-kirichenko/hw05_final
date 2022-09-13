from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render, get_object_or_404

from .forms import CommentForm, PostForm
from .models import Follow, Post, Group, User
from users.models import UserProfile

from yatube.settings import POSTS_PER_PAGE


def get_paginator_page(request, post_list):
    """Возвращает текущую страницу с постами.

    Args:
        request (HttpRequest): объект запроса.
        post_list (QuerySet): список постов.

    Returns:
        Page: объект текущей страницы.
    """

    return Paginator(post_list, POSTS_PER_PAGE).get_page(
        request.GET.get('page')
    )


def index(request):
    """Возвращает ответ с главной страницей с постами.

    Args:
        request (HttpRequest): объект запроса.

    Returns:
        HttpResponse: объект ответа.
    """

    return render(request, 'posts/index.html', {
        'page_obj': get_paginator_page(
            request, Post.objects.select_related('author', 'group').all()
        )}
    )


def group_posts(request, slug):
    """Возвращает ответ со страницей с постами группы.

    Args:
        request (HttpRequest): объект запроса.
        slug (str): уникальное название группы латиницей.

    Returns:
        HttpResponse: объект ответа.
    """

    group = get_object_or_404(Group, slug=slug)
    return render(request, 'posts/group_list.html', {
        'group': group,
        'page_obj': get_paginator_page(
            request, group.posts.select_related('author').all()
        )}
    )


def profile(request, username):
    """Возвращает ответ со страницей с постами пользователя.

    Args:
        request (HttpRequest): объект запроса.
        username (str): имя пользователя.

    Returns:
        HttpResponse: объект ответа.
    """

    author = get_object_or_404(User, username=username)
    UserProfile.objects.get_or_create(user=author)
    following = (
        request.user.is_authenticated and author != request.user
        and Follow.objects.filter(
            author=author,
            user=request.user
        ).exists()
    )
    return render(request, 'posts/profile.html', {
        'author': author,
        'page_obj': get_paginator_page(
            request, author.posts.select_related('group').all()
        ),
        'following': following,
    })


def post_detail(request, post_id):
    """Возвращает ответ со страницей отдельного поста.

    Args:
        request (HttpRequest): объект запроса.
        post_id (int): id поста.

    Returns:
        HttpResponse: объект ответа.
    """

    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'form': form,
    })


@login_required
def post_create(request):
    """Создаёт пост.

    Args:
        request (HttpRequest): объект запроса.

    Returns:
        HttpResponse: объект ответа со страницей создания поста если данные
        внесенные в форму не корректны.
    Returns:
        HttpResponseRedirect: перенаправляет на страницу профиля пользователя
        создавшего пост если данные введенные в форму корректны.
    """

    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {
            'form': form
        })
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=post.author.username)


@login_required
def post_edit(request, post_id):
    """Редактирует пост.

    Args:
        request (HttpRequest): объект запроса.
        post_id (int): id поста.

    Returns:
        HttpResponseRedirect: перенаправляет на страницу поста если
        пользователь не является автором.
    Returns:
        HttpResponse: объект ответа со страницей создания поста если данные
        внесенные в форму не корректны.
    Returns:
        HttpResponseRedirect: перенаправляет на страницу созданного поста если
        данные внесенные в форму корректны.
    """

    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {
            'form': form,
            'post': post,
            'is_edit': True
        })
    post = form.save()
    return redirect('posts:post_detail', post_id=post.id)


@login_required
def add_comment(request, post_id):
    """Добавляет комментарий.

    Args:
        request (HttpRequest): объект запроса.
        post_id (int): id поста.

    Returns:
        HttpResponseRedirect: перенаправляет на страницу поста если данные
        внесенные в форму корректны.
    """

    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Возвращает ответ со страницей с постами пользователей на которых
    подписан текущий пользователь.

    Args:
        request (HttpRequest): объект запроса.

    Returns:
        HttpResponse: объект ответа.
    """

    post_list = Post.objects.select_related('author', 'group').filter(
        author__following__user=request.user
    )
    context = {
        'page_obj': get_paginator_page(request, post_list)
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписывает на пользователя.

    Args:
        request (HttpRequest): объект запроса.
        username (str): имя пользователя на которого подписываются.

    Returns:
        HttpResponseRedirect: перенаправляет на страницу профиля пользователя
        при успешной подписке на него.
    """

    author = get_object_or_404(User, username=username)
    if (author != request.user
        and not Follow.objects.filter(user=request.user,
                                      author=author).exists()):
        Follow.objects.create(
            user=request.user,
            author=author,
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Отписывает от пользователя.

    Args:
        request (HttpRequest): объект запроса.
        username (str): имя пользователя от которого отписываются.

    Returns:
        HttpResponseRedirect: перенаправляет на страницу профиля пользователя
        при успешной отписке от него.
    """

    get_object_or_404(Follow, user=request.user,
                      author__username=username).delete()
    return redirect('posts:profile', username=username)
