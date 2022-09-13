from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import UserProfile


class CreationForm(UserCreationForm):
    """Форма для создания пользователя."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class UserProfileForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя."""

    class Meta:
        model = UserProfile
        fields = ('about', 'avatar')
