from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView

from blog.forms import BlogForm
from blog.models import Blog


# Обобщенное представление для просмотра списка объектов модели Blog
class BlogListView(ListView):
    model = Blog
    queryset = Blog.objects.filter(published_on=True)


# Обобщенное представление для создания нового объекта модели Blog
class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Blog
    form_class = BlogForm
    success_url = reverse_lazy('blog:blog_list')


# Обобщенное представление для просмотра деталей объекта модели Blog
class BlogDetailView(LoginRequiredMixin, DetailView):
    model = Blog

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        obj.views += 1
        obj.save()
        return obj


# Обобщенное представление для обновления объекта модели Blog
class BlogUpdateView(LoginRequiredMixin, UpdateView):
    model = Blog
    form_class = BlogForm
    success_url = reverse_lazy('blog:blog_list')

    def get_success_url(self):
        return self.object.get_absolute_url()


# Обобщенное представление для удаления объекта модели Blog
class BlogDeleteView(LoginRequiredMixin, DeleteView):
    model = Blog
    success_url = reverse_lazy('blog:blog_list')


@permission_required('blog.set_published_blog')
def toggle_activity(request, slug):
    record_item = get_object_or_404(Blog, slug=slug)
    record_item.toggle_published()
    return redirect(reverse('blog:blog_detail', args=[record_item.slug]))
