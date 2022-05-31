from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView

from django.urls import reverse_lazy

from .forms import CreationForm, UserProfileForm
from .models import UserProfile


class SignUp(UserPassesTestMixin, CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'

    def test_func(self):
        return self.request.user.is_anonymous


@login_required
def user_profile_form(request, username):
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
        return render(request, 'users/user_profile_form.html', {
            'form': form,
            'user_profile': user_profile,
        })
    user_profile = form.save()
    return redirect('posts:profile', username=username)
