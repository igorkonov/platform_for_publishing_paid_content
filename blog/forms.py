from django import forms

from blog.models import Blog, Comment


class StyleFormMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class BlogForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Blog
        fields = '__all__'
        exclude = ('slug', 'views', 'user', 'comments')


class BlogAdminForm(forms.ModelForm):
    class Meta:
        model = Blog
        exclude = ['comments']

class CommentForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
