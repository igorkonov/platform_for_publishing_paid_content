from django.contrib import admin
from subscriptions.models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
        Административное представление для модели Subscription.
        Определено поле list_display для отображения в списке записей модели.
    """
    list_display = ('id', 'blog', 'user', 'status', 'payment_status', 'payment_date',)
