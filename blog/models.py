from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from transliterate import translit
# Create your models here.
NULLABLE = {'blank': True, 'null': True}


class Blog(models.Model):
    title = models.CharField(max_length=150, verbose_name='Заголовок')
    slug = models.SlugField(max_length=150, unique=True, verbose_name='Slug')
    description = models.TextField(verbose_name='Описание контента')
    image = models.ImageField(upload_to='blog/', **NULLABLE, verbose_name='Изображение')
    created_date = models.DateField(auto_now_add=True, verbose_name='Дата публикации')
    views = models.IntegerField(verbose_name='Количество просмотров', default=0, **NULLABLE)
    published_on = models.BooleanField(default=False, verbose_name='Дата публикации')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, **NULLABLE,
                             verbose_name='Автор контента')
    price = models.IntegerField(default=0, verbose_name='Стоимость подписки')
    comment = models.TextField(verbose_name='Комментарий')

    class Meta:
        verbose_name = 'Контент'
        verbose_name_plural = 'Контенты'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:blog_detail', kwargs={'slug': self.slug})

    def toggle_published(self):
        self.published_on = not self.published_on
        self.save()

    def save(self, *args, **kwargs):
        if not self.slug:
            transliterated_title = translit(self.title, 'ru', reversed=True)
            self.slug = slugify(transliterated_title, allow_unicode=True)
        super().save(*args, **kwargs)
