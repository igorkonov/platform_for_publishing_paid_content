from django import forms
from blog.models import Blog, Comment


class StyleFormMixin:
    """
        Миксин для форм, добавляющий класс 'form-control' к виджетам полей.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class BlogForm(StyleFormMixin, forms.ModelForm):
    """
        Форма для модели Blog.
    """
    class Meta:
        model = Blog
        fields = ['title', 'description', 'image', 'published_on', 'price', 'is_paid']
        exclude = ('slug', 'views', 'user', 'comments')


class BlogAdminForm(forms.ModelForm):
    """
        Форма для администрирования модели Blog.
    """
    class Meta:
        model = Blog
        exclude = ['comments']


class CommentForm(StyleFormMixin, forms.ModelForm):
    """
        Форма для модели Comment.
    """
    class Meta:
        model = Comment
        fields = ['comment']
