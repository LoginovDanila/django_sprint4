from django import forms
from django.contrib.auth.forms import UserChangeForm

from .models import Comment, Post, User


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'datetime-local'})
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
