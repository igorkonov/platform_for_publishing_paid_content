from django.conf import settings
from django.db import models

from blog.models import NULLABLE, Blog


class Payments(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, **NULLABLE, on_delete=models.CASCADE, verbose_name='Пользователь')
    payment_date = models.DateField(auto_now_add=True, verbose_name='Дата платежа')
    paid_blog = models.ForeignKey(Blog, on_delete=models.CASCADE, **NULLABLE, verbose_name='Оплаченный контент')
    payment_amount = models.PositiveIntegerField(verbose_name='Сумма платежа')
    payment_intent_id = models.CharField(max_length=500, **NULLABLE, verbose_name='ID намерения платежа')
    payment_method_id = models.CharField(max_length=500, **NULLABLE, verbose_name='ID метода платежа')
    status = models.CharField(max_length=50, **NULLABLE, verbose_name='Статус платежа')
    confirmation = models.BooleanField(default=False, verbose_name='Подтверждение платежа')

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'

    def __str__(self):
        return f'{self.user}: {self.paid_blog}'
