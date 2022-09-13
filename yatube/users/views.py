from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView

from django.urls import reverse_lazy

from .forms import CreationForm, UserProfileForm
from .models import UserProfile


class SignUp(UserPassesTestMixin, CreateView):
    """View класс для регистрации пользователя."""

    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'

    def test_func(self):
        """Проверяет является ли пользователь анонимом.

        Returns:
            bool: True если пользователь аноним иначе False.
        """

        return self.request.user.is_anonymous


@login_required
def user_profile_form(request, username):
    """Редактирование профиля пользователя.

    Args:
        request (HttpRequest): объект запроса.
        username (str): имя пользователя.

    Returns:
        HttpResponseRedirect: перенаправляет на страницу профиля пользователя
        если это профиль не текущего пользователя.
    Returns:
        HttpResponse: открывает страницу редактирования профиля заного если
        данные внесенные в форму были не корректны.
    Returns:
        HttpResponseRedirect: перенаправляет на страницу профиля пользователя
        создавшего пост если данные введенные в форму корректны.
    """

    author = get_object_or_404(User, username=username)
    user_profile = get_object_or_404(UserProfile, user=author)
    if user_profile.user != request.user:
        return redirect('posts:profile', username=username)
    form = UserProfileForm(
        request.POST or None,
        files=request.FILES or None,
        instance=user_profile
    )
    if not form.is_valid():
        return render(request, 'users/user_profile_form.html', {'form': form})
    user_profile = form.save()
    return redirect('posts:profile', username=username)
