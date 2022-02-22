from django import forms

from .models import Follow, Post, Comment

from django.utils.translation import gettext_lazy as _


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        labels = {
            'text': _('Writer'),
        }
        help_texts = {
            'text': _('Текст нового поста'),
        }
        widgets = {
            "text": forms.Textarea(attrs={
                'class': 'form-control',
                'cols': '40',
                'rows': '10'
            }),
            'group': forms.Select(attrs={
                'class': 'form-control',
            })
        }


class CommentForm(forms.ModelForm):
    """Форма для добавления комментария."""
    class Meta:
        model = Comment
        fields = {'text'}
        labels = {'text': 'Текст'}


class FollowForm(forms.ModelForm):
    """Форма подписки на авторов."""
    class Meta:
        model = Follow
        fields = {'user'}
        labels = {'Пользователь подписывается на:'}
