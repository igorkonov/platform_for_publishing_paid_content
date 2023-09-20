from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, TemplateView
from blog.forms import BlogForm, CommentForm
from blog.models import Blog, Comment
from subscriptions.models import Subscription


class HomePageView(TemplateView):
    """
        Контроллер для отображения главной страницы.

        Атрибуты:
            template_name (str): Путь к HTML-шаблону.

        Методы:
            get_context_data(**kwargs): Возвращает контекстные данные для отображения в шаблоне.
    """

    template_name = 'blog/home.html'

    def get_context_data(self, **kwargs):
        """
            Получает контекстные данные для отображения в шаблоне.

            Возвращает:
                dict: Словарь с контекстными данными.
        """
        context_data = super().get_context_data(**kwargs)
        context_data['blog'] = Blog.objects.filter(published_on=True).order_by('?')[:3]

        if self.request.user.is_authenticated:
            user = self.request.user

            # Получение списка идентификаторов блогов, на которые подписан пользователь
            subscribed_blog_ids = Subscription.objects.filter(user=user, status=True).values_list('blog__id', flat=True)

            # Получаем блоги, на которые пользователь не подписан
            unsubscribed_blogs = Blog.objects.filter(published_on=True).exclude(id__in=subscribed_blog_ids)

            # Получаем блоги, на которые подписан пользователь
            subscribed_blogs = Blog.objects.filter(id__in=subscribed_blog_ids, published_on=True)

            context_data['unsubscribed_blogs'] = unsubscribed_blogs
            context_data['subscribed_blogs'] = subscribed_blogs

        return context_data


class BlogListView(ListView):
    """
        Контроллер для отображения списка объектов Blog.

        Атрибуты:
            model (Model): Модель, используемая для этого контроллера.
            template_name (str): Путь к HTML-шаблону.

        Методы:
            get_queryset(): Возвращает набор данных объектов Blog для отображения.
    """

    model = Blog
    template_name = 'blog_list.html'

    def get_queryset(self):

        user = self.request.user

        # Получение списка идентификаторов блогов, на которые подписан пользователь
        subscribed_blog_ids = Subscription.objects.filter(user=user, status=True).values_list('blog__id', flat=True)

        # Получаем блоги, на которые пользователь не подписан и не является их автором
        unsubscribed_blogs = Blog.objects.filter(published_on=True).exclude(id__in=subscribed_blog_ids).exclude(user=user)

        return unsubscribed_blogs


class BlogCreateView(LoginRequiredMixin, CreateView):
    """
        Контроллер для создания нового объекта Blog.

        Атрибуты:
            model (Model): Модель, используемая для этого контроллера.
            form_class (Form): Класс формы, используемый для этого контроллера.
            success_url (str): URL для перенаправления после успешной отправки формы.

        Методы:
            form_valid(form): Обрабатывает отправку формы и создает новый объект Blog.
    """

    model = Blog
    form_class = BlogForm
    success_url = reverse_lazy('blog:blog_list')

    def form_valid(self, form):
        if form.is_valid():
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            self.object.save()
        return super().form_valid(form)


class BlogDetailView(LoginRequiredMixin, DetailView):
    """
        Контроллер для отображения подробностей объекта Blog.

        Атрибуты:
            model (Model): Модель, используемая для этого контроллера.
            form_class (Form): Класс формы для комментариев.
            template_name (str): Путь к HTML-шаблону.

        Методы:
            get_object(queryset=None): Возвращает объект Blog для этого контроллера.
            get_context_data(**kwargs): Возвращает контекстные данные для отображения в шаблоне.
            post(request, *args, **kwargs): Обрабатывает отправку комментария.
    """

    model = Blog
    form_class = CommentForm
    template_name = 'blog/blog_detail.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        obj.views += 1
        obj.save()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(blog=self.object)
        return context

    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)

        if form.is_valid():
            comment_content = form.cleaned_data['comment']
            comment = Comment.objects.create(user=request.user, comment=comment_content)

            blog = self.get_object()
            blog.comments.add(comment)
            blog.save()

        return HttpResponseRedirect(self.request.path_info)


class BlogUpdateView(LoginRequiredMixin, UpdateView):
    """
        Контроллер для обновления существующего объекта Blog.

        Атрибуты:
            model (Model): Модель, используемая для этого контроллера.
            form_class (Form): Класс формы, используемый для этого контроллера.
            success_url (str): URL для перенаправления после успешного обновления.

        Методы:
            get_success_url(): Возвращает URL для перенаправления после успешного обновления.
    """

    model = Blog
    form_class = BlogForm
    success_url = reverse_lazy('blog:blog_list')

    def get_success_url(self):
        return self.object.get_absolute_url()


class BlogDeleteView(LoginRequiredMixin, DeleteView):
    """
        Контроллер для удаления существующего объекта Blog.

        Атрибуты:
            model (Model): Модель, используемая для этого контроллера.
            success_url (str): URL для перенаправления после успешного удаления.
    """

    model = Blog
    success_url = reverse_lazy('blog:blog_list')


def toggle_activity(request, slug):
    """
        Переключает атрибут 'published_on' объекта Blog.

        Args:
            request (HttpRequest): Объект HTTP-запроса.
            slug (str): Слаг объекта Blog.

        Returns:
            HttpResponseRedirect: Перенаправляет на страницу деталей объекта Blog.
    """
    record_item = get_object_or_404(Blog, slug=slug)
    record_item.toggle_published()
    return redirect(reverse('blog:blog_detail', args=[record_item.slug]))
