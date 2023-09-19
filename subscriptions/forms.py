from django import forms
from django.utils import timezone
from blog.forms import StyleFormMixin
from subscriptions.models import Subscription


class SubscriptionForm(StyleFormMixin, forms.ModelForm):
    """
        Форма для оформления подписки.
        fields (list): Список полей формы (пустой, так как все поля заполняются в методе create_subscription).

        Methods:
            create_subscription(user, blog): Создает подписку и сохраняет в базу данных.
    """

    class Meta:
        model = Subscription
        fields = []

    def create_subscription(self, user, blog):
        """
            Создает и сохраняет подписку в базу данных.

            Args:
                user (User): Пользователь, оформляющий подписку.
                blog (Blog): Контент, на который оформляется подписка.
        """
        subscription = self.save(commit=False)
        subscription.user = user
        subscription.blog = blog
        subscription.status = True
        subscription.payment_status = True
        subscription.payment_date = timezone.now()
        subscription.save()
