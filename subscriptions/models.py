from django.db import models

from blog.models import Blog
from payments.models import Payments
from users.models import User


# Create your models here.
class Subscription(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, verbose_name='Контент')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    payment = models.ForeignKey(Payments, on_delete=models.CASCADE, verbose_name='Платеж')
    status = models.BooleanField(default=False, verbose_name='Статус подписки')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} - {self.blog}: {self.status}'
