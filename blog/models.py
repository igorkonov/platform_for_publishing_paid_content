from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from transliterate import translit

NULLABLE = {'blank': True, 'null': True}


class Comment(models.Model):
    """
        Модель для хранения комментариев к блогам.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    comment = models.TextField(verbose_name='Коммент')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Время отправки комментария')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.comment


class Blog(models.Model):
    """
        Модель для представления контента блога.
    """
    title = models.CharField(max_length=150, verbose_name='Заголовок')
    slug = models.SlugField(max_length=150, unique=True, verbose_name='Slug')
    description = models.TextField(verbose_name='Описание контента')
    image = models.ImageField(upload_to='blog/', **NULLABLE, verbose_name='Изображение')
    created_date = models.DateField(auto_now_add=True, verbose_name='Дата публикации')
    views = models.IntegerField(verbose_name='Количество просмотров', default=0, **NULLABLE)
    published_on = models.BooleanField(default=False, verbose_name='Признак публикации')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, **NULLABLE,
                             verbose_name='Автор контента')
    price = models.IntegerField(default=0, verbose_name='Стоимость подписки')
    is_paid = models.BooleanField(default=False, verbose_name='Платный контент')
    comments = models.ManyToManyField(Comment, blank=True, verbose_name='Комментарии')

    class Meta:
        verbose_name = 'Контент'
        verbose_name_plural = 'Контенты'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
            Переопределение метода сохранения объекта.
            Если у объекта нет slug, то генерируется транслитерированный slug из заголовка.
        """
        if not self.slug:
            transliterated_title = translit(self.title, 'ru', reversed=True)
            self.slug = slugify(transliterated_title, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """
            Возвращает абсолютный URL для просмотра объекта.
        """
        return reverse('blog:blog_detail', kwargs={'slug': self.slug})

    def toggle_published(self):
        """
            Переключает признак публикации блога.
        """
        self.published_on = not self.published_on
        self.save()

    def get_display_price(self):
        """
            Возвращает цену в формате с двумя десятичными знаками.
        """
        return "{0:.2f}".format(self.price / 100)
